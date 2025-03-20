from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150),nullable=False)
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user', lazy=True)  

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))  # Field for note content
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    completed = db.Column(db.Boolean, default=False)  # Field to track completion
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User model