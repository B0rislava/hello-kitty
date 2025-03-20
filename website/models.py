from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150),nullable=False)
    first_name = db.Column(db.String(150))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    answers = db.relationship('Answer', backref='question', lazy=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)


    @staticmethod
    def create_answer(question_id, answer_text, is_correct=False):
        new_answer = Answer(question_id=question_id, text=answer_text, is_correct=is_correct)
        db.session.add(new_answer)
        db.session.commit()
        return new_answer