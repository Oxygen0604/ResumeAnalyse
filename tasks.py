from celery import Celery
from manager import create_app
from services import AnalysisService

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

app = create_app()
celery = make_celery(app)

@celery.task(name='analyze_resume')
def analyze_resume_task(resume_id):
    """异步分析任务"""
    with app.app_context():
        success, message = AnalysisService.process_resume(resume_id)
        if not success:
            app.logger.error(f"简历分析失败: {message}")