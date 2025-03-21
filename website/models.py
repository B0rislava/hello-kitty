from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150),nullable=False)
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user', lazy=True) 
    streak_record = db.Column(db.Integer, default=0) 
    last_active = db.Column(db.Date, default=datetime.utcnow().date())

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000)) 
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    completed = db.Column(db.Boolean, default=False)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   

class DailyChallenges(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meditation_duration = db.Column(db.Integer, nullable = False)
    meditation_completed = db.Column(db.Boolean, default = False)
    meditation_timestamp = db.Column(db.DateTime, nullable = False)
    user = db.relationship('User', backref='daily_challenges', lazy=True)

class SleepTime(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sleeptime_from = db.Column(db.DateTime, nullable = True)
    sleeptime_to = db.Column(db.DateTime, nullable = False)