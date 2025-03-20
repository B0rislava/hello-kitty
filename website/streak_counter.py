from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from .models import User, Note
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

def update_streak(user):
    today = datetime.utcnow().date()

    if user.last_active == today:
        return 
    
    incomplete_notes = Note.query.filter_by(user_id=user.id, completed=False).count()

    if incomplete_notes == 0:
        if user.last_active == today - timedelta(days=1):
            user.streak=+ 1
        else:
            user.streak = 1

        user.last_active = today
        db.session.commit

@app.route('/activity', methods=['POST'])
def record_activity():
    data = request.json
    first_name = request.get('first_name')
    user = User.query.filter_by(first_name=first_name).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    update_streak(user)
    return jsonify({'message': 'Activity recorded', 'streak': user.streak})

