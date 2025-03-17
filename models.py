from datetime import datetime
from manager import db
from flask import Flask, current_app
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """用户表模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False, default='job_seeker')

    # 建立与简历表的一对多关系
    resumes = db.relationship('Resume', backref='user', lazy='dynamic')

    @validates('role')
    def validate_role(self, key, role):
        """验证用户角色"""
        if role not in current_app.config['ALLOWED_ROLES']:
            raise ValueError(f'Invalid role: {role}')
        return role


class Resume(db.Model):
    """简历表模型"""
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='未处理')  # 状态：未处理/已处理

    # 建立关联关系
    resume_info = db.relationship('ResumeInfo', backref='resume', uselist=False)
    job_matches = db.relationship('JobMatch', backref='resume', lazy='dynamic')


class ResumeInfo(db.Model):
    """简历关键信息表模型"""
    __tablename__ = 'resume_info'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    career_interest = db.Column(db.String(100))
    education = db.Column(db.JSON)
    experience = db.Column(db.JSON)
    skills = db.Column(db.JSON)
    self_evaluation = db.Column(db.JSON)

    __table_args__ = (
        db.Index('idx_resume_id', 'resume_id'),  # 建立索引
    )


class JobMatch(db.Model):
    """职位匹配表模型"""
    __tablename__ = 'jobmatches'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    position_match = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    match_score = db.Column(db.Numeric(5, 2))
    analysis_result = db.Column(db.JSON)

    # 建立组合索引
    __table_args__ = (
        db.Index('idx_resume_position', 'resume_id', 'position_match'),
    )


# 数据库初始化函数
def init_db():
    db.create_all()


def drop_db():
    db.drop_all()