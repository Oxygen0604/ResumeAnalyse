import os
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from werkzeug.utils import secure_filename
import json
from models import db, User, Resume, ResumeInfo, JobMatch


class UserService:
    """用户相关服务"""

    @staticmethod
    def create_user(user_data: Dict) -> Tuple[Optional[User], str]:
        """创建用户并加密密码"""
        try:
            if User.query.filter_by(username=user_data['username']).first():
                return None, "用户名已存在"

            hashed_pw = generate_password_hash(user_data['password'])
            new_user = User(
                username=user_data['username'],
                password=hashed_pw,
                email=user_data.get('email'),
                role=user_data.get('role', 'job_seeker')
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user, ""
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user
        return None


class ResumeService:
    """简历处理服务"""

    @staticmethod
    def save_upload_file(file, user_id: int) -> Tuple[Optional[Resume], str]:
        """保存上传文件并创建记录"""
        try:
            filename = secure_filename(file.filename)
            if not allowed_file(filename):
                return None, "不支持的文件类型"

            # 生成存储路径
            save_dir = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                str(user_id)
            )
            os.makedirs(save_dir, exist_ok=True)

            # 生成唯一文件名
            new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            save_path = os.path.join(save_dir, new_filename)
            file.save(save_path)

            # 创建简历记录
            new_resume = Resume(
                user_id=user_id,
                file_path=save_path,
                status='未处理'
            )
            db.session.add(new_resume)
            db.session.commit()
            return new_resume, ""
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def trigger_analysis(resume_id: int):
        """触发简历分析（异步）"""
        from tasks import analyze_resume_task  # 导入异步任务
        resume = Resume.query.get(resume_id)
        if not resume:
            return False, "简历不存在"

        try:
            resume.status = '处理中'
            db.session.commit()
            analyze_resume_task.delay(resume_id)  # 发送到Celery任务队列
            return True, ""
        except Exception as e:
            db.session.rollback()
            return False, str(e)


class AnalysisService:
    """简历分析服务"""
    @staticmethod
    def process_resume(resume_id: int) -> Tuple[bool, str]:

        try:
            resume = Resume.query.get_or_404(resume_id)

            # 获取完整分析结果（包含推荐职位）
            api_result = AnalysisService._call_deepseek_api_with_matches(resume.file_path)
            if not api_result['success']:
                return False, "API解析失败"

            # 解析数据
            parsed_data = AnalysisService._parse_full_api_data(api_result['data'])
            if not parsed_data:
                return False, "数据解析异常"

            # 保存所有结果
            AnalysisService._save_full_analysis(resume_id, parsed_data)

            # 更新状态
            resume.status = '已处理'
            resume.processed_at = datetime.utcnow()
            db.session.commit()

            return True, "分析成功"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"处理失败: {str(e)}")
            return False, str(e)

    @staticmethod
    def _call_deepseek_api_with_matches(file_path: str) -> Dict:

        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    current_app.config['DEEPSEEK_API_URL'],
                    headers={
                        'Authorization': f'Bearer {current_app.config["DEEPSEEK_API_KEY"]}',
                        'X-Require-Matches': 'true'  # 要求返回匹配职位
                    },
                    files={'resume': f},
                    timeout=30
                )

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}

            current_app.logger.error(f"API错误: {response.status_code}")
            return {'success': False}
        except Exception as e:
            current_app.logger.error(f"API调用异常: {str(e)}")
            return {'success': False}

    @staticmethod
    def _parse_full_api_data(raw_data: Dict) -> Optional[Dict]:
        """ 解析包含职位推荐的API响应 """
        try:
            # 基础信息
            basic = raw_data.get('basic_info', {})
            contact = basic.get('contact', {})

            # 推荐职位
            matches = []
            for match in raw_data.get('analysis', {}).get('matched_positions', []):
                matches.append({
                    'position': match.get('position'),
                    'salary_range': match.get('salary_range'),
                    'match_score': float(match.get('match_rate', 0)) * 100,
                    'analysis': match.get('reason', '')
                })

            return {
                # 基本信息
                'name': basic.get('name'),
                'age': basic.get('age'),
                'contact': {
                    'phone': contact.get('phone'),
                    'email': contact.get('email')
                },
                'education': raw_data.get('education', []),
                'experience': raw_data.get('experience', []),
                'skills': raw_data.get('skills', []),
                'self_evaluation': raw_data.get('summary', ''),

                # API推荐的职位
                'matches': sorted(matches, key=lambda x: x['match_score'], reverse=True)[:5]
            }
        except Exception as e:
            current_app.logger.error(f"解析失败: {str(e)}")
            return None

    @staticmethod
    def _save_full_analysis(resume_id: int, data: Dict):
        """保存完整分析结果"""
        with db.session.begin_nested():
            # 保存基本信息
            ResumeInfo.query.filter_by(resume_id=resume_id).delete()
            resume_info = ResumeInfo(
                resume_id=resume_id,
                name=data['name'],
                age=data['age'],
                phone=data['contact']['phone'],
                email=data['contact']['email'],
                education=json.dumps(data['education'], ensure_ascii=False),
                experience=json.dumps(data['experience'], ensure_ascii=False),
                skills=json.dumps(data['skills'], ensure_ascii=False),
                self_evaluation=data['self_evaluation']
            )
            db.session.add(resume_info)

            # 保存匹配结果
            JobMatch.query.filter_by(resume_id=resume_id).delete()
            for match in data.get('matches', []):
                job_match = JobMatch(
                    resume_id=resume_id,
                    position_match=match['position'],
                    salary_range=match['salary_range'],
                    match_score=match['match_score'],
                    analysis_result=match['analysis']
                )
                db.session.add(job_match)

            db.session.commit()


class ApiResult:
    """API调用结果封装"""

    def __init__(self, success: bool, data=None):
        self.success = success
        self.data = data


# 工具函数
def allowed_file(filename: str) -> bool:
    """验证文件扩展名"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']