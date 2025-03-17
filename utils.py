import uuid
from flask import Flask, current_app

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    allowed_ext = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext

def generate_filename(original_name):
    """生成唯一文件名"""
    ext = original_name.split('.')[-1]
    return f"{uuid.uuid4().hex}.{ext}"