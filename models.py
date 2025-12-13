from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")
    avatar = db.Column(db.String(100), default="avatar1.jpg")
    saved_xp = db.Column(db.Integer, default=0)
    saved_level = db.Column(db.Integer, default=1)
    saved_streak = db.Column(db.Integer, default=0)
    study_logs = db.relationship('StudyLog', backref='user', lazy=True)
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', role='{self.role}')"

class StudyLog(db.Model):
    __tablename__ = 'study_log'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    def __repr__(self):
        return (f"StudyLog(id={self.id}, subject='{self.subject}', minutes={self.minutes}, "
                f"date='{self.date}', user_id={self.user_id})")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(50), nullable=False)
    goal_type = db.Column(db.String(10), default="weekly")
    goal_minutes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Subject {self.name}>"
