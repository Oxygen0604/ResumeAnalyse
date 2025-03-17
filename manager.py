import os
import click
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import DevelopmentConfig, ProductionConfig


# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()


def create_app(env='development'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    app.config.from_object(config_map.get(env, DevelopmentConfig))

    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)

    # 注册蓝图
    from routes import bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # 确保上传目录存在
    with app.app_context():
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

    return app


@click.group()
def cli():
    """命令行入口"""
    pass


@cli.command()
@click.option('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
@click.option('--port', default=5000, help='监听端口 (默认: 5000)')
@click.option('--env', default='development', help='配置环境 (development/production)')
def run(host, port, env):
    """启动开发服务器"""
    app = create_app(env)
    app.run(host=host, port=port, debug=(env == 'development'))


@cli.command()
@click.option('--env', default='development', help='配置环境')
@click.option('--drop/--no-drop', default=False, help='是否删除旧数据库')
def initdb(env, drop):
    """初始化数据库"""
    app = create_app(env)
    with app.app_context():
        if drop:
            db.drop_all()
            click.echo("已删除旧数据库")
        db.create_all()
        click.echo("数据库初始化完成")


@cli.command()
@click.option('--env', default='development', help='配置环境')
def migrate(env):
    """生成迁移脚本"""
    from flask_migrate import migrate as _migrate
    app = create_app(env)
    with app.app_context():
        _migrate()
        click.echo("迁移脚本已生成")


@cli.command()
@click.option('--env', default='development', help='配置环境')
def test(env):
    """运行测试"""
    app = create_app(env)
    with app.app_context():
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover('tests', pattern='test*.py')
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_runner.run(test_suite)


if __name__ == '__main__':
    cli()