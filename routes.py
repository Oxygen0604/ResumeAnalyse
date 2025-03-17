from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import timedelta
import os

from utils import allowed_file, generate_filename



# 创建蓝图
bp = Blueprint('api', __name__, url_prefix='/api')

def allowed_file(filename):
    """验证文件扩展名"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# 辅助函数
def validate_json(schema, data):
    """JSON数据验证"""
    missing = [field for field in schema if field not in data]
    if missing:
        return False, f"缺少必要字段: {', '.join(missing)}"
    return True, ""

# 用户认证相关路由
@bp.route('/register', methods=['POST'])
def register():
    from models import db, User
    """用户注册"""
    data = request.get_json()
    valid, msg = validate_json(['username', 'password'], data)
    if not valid:
        return jsonify({"error": msg}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "用户名已存在"}), 409

    try:
        new_user = User(
            username=data['username'],
            password=generate_password_hash(data['password']),
            email=data.get('email'),
            role=data.get('role', 'job_seeker')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    from models import User
    """用户登录"""
    data = request.get_json()
    valid, msg = validate_json(['username', 'password'], data)
    if not valid:
        return jsonify({"error": msg}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not check_password_hash(user.password, data['password']):
        return jsonify({"error": "无效的用户名或密码"}), 401

    expires = timedelta(hours=2)
    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role},
        expires_delta=expires
    )
    return jsonify(access_token=access_token), 200


# 简历管理路由
@bp.route('/resumes/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    from models import db, Resume
    """上传简历文件"""
    if 'file' not in request.files:
        return jsonify({"error": "未上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "无效的文件名"}), 400

    # 安全处理文件名
    original_filename = secure_filename(file.filename)

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件类型"}), 415

    try:
        # 获取配置中的上传路径
        upload_dir = bp.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        # 生成存储路径
        user_id = get_jwt_identity()
        filename = generate_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        file.save(save_path)

        # 创建简历记录
        new_resume = Resume(
            user_id=user_id,
            file_path=save_path,
            status='未处理'
        )
        db.session.add(new_resume)
        db.session.commit()

        # 构造响应
        response = make_response(jsonify({
            'message': '文件上传成功',
            'stored_path': save_path
        }))

        # 添加自定义响应头
        response.headers['X-Original-Filename'] = original_filename

        # 允许前端访问自定义头
        response.headers.add('Access-Control-Expose-Headers', 'X-Original-Filename')

        return response

    except Exception as e:
        bp.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': '服务器处理文件失败'}), 500





@bp.route('/resumes', methods=['GET'])
@jwt_required()
def get_resumes():
    from models import Resume
    """获取当前用户的简历列表"""
    user_id = get_jwt_identity()
    resumes = Resume.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": r.id,
        "upload_time": r.upload_time.isoformat(),
        "status": r.status
    } for r in resumes]), 200


@bp.route('/resumes/<int:resume_id>', methods=['GET'])
@jwt_required()
def get_resume_detail(resume_id):
    from models import Resume
    """获取简历详情"""
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != get_jwt_identity():
        return jsonify({"error": "无权访问"}), 403

    return jsonify({
        "id": resume.id,
        "file_path": resume.file_path,
        "status": resume.status,
        "upload_time": resume.upload_time.isoformat()
    }), 200


# 数据分析路由
@bp.route('/resumes/<int:resume_id>/analysis', methods=['GET'])
@jwt_required()
def get_analysis(resume_id):
    from models import Resume, ResumeInfo
    """获取分析结果"""
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != get_jwt_identity():
        return jsonify({"error": "无权访问"}), 403

    analysis = ResumeInfo.query.filter_by(resume_id=resume_id).first()
    if not analysis:
        return jsonify({"error": "分析结果不存在"}), 404

    return jsonify({
        "basic_info": {
            "name": analysis.name,
            "age": analysis.age,
            "contact": {
                "email": analysis.email,
                "phone": analysis.phone
            }
        },
        "career_interest": analysis.career_interest,
    }), 200


@bp.route('/resumes/<int:resume_id>/matches', methods=['GET'])
@jwt_required()
def get_job_matches(resume_id):
    from models import JobMatch
    """获取职位匹配结果"""
    matches = JobMatch.query.filter_by(resume_id=resume_id).all()
    return jsonify([{
        "position": m.position_match,
        "salary_range": m.salary_range,
        "match_score": str(m.match_score),
        "analysis": m.analysis_result
    } for m in matches]), 200


# 管理员路由
@bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    from models import User
    """获取所有用户（仅管理员）"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({"error": "权限不足"}), 403

    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "role": u.role
    } for u in users]), 200


@bp.route('/admin/resumes', methods=['GET'])
@jwt_required()
def get_all_resumes():
    from models import Resume
    """获取所有简历（仅管理员）"""
    if get_jwt().get('role') != 'admin':
        return jsonify({"error": "权限不足"}), 403

    resumes = Resume.query.all()
    return jsonify([{
        "id": r.id,
        "user_id": r.user_id,
        "status": r.status
    } for r in resumes]), 200


# 错误处理
@bp.errorhandler(404)
def handle_not_found(e):
    return jsonify(error="资源不存在"), 404


@bp.errorhandler(500)
def handle_server_error(e):
    return jsonify(error="服务器内部错误"), 500