import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录下的.env文件
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """基础配置类"""
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')  # 用于加密的密钥

    # 数据库配置（MySQL示例）
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}'.format(
        user=os.getenv('DB_USER', 'root'),  # 数据库用户名
        password=os.getenv('DB_PASSWORD', '12345'),  # 数据库密码
        host=os.getenv('DB_HOST', 'localhost'),  # 数据库地址
        port=os.getenv('DB_PORT', '3306'),
        dbname=os.getenv('DB_NAME', 'resume_database')  # 数据库名称
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭修改跟踪

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')  # 上传文件存储路径
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # 允许的文件类型
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 限制上传文件大小5MB

    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
    DEEPSEEK_API_URL = 'https://api.deepseek.com'
    # 角色验证配置
    ALLOWED_ROLES = ['job_seeker', 'admin', 'hr']  # 允许的角色类型

    # 异步任务配置
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///example.db'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_POOL_RECYCLE = 299  # 连接池回收时间
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host/dbname'
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'


# 配置环境映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}