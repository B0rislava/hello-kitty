from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required
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
        if user.streak_record == today - timedelta(days=1):
            user.streak_record=+ 1
        else:
            user.streak_record = 1

        user.last_active = today
        db.session.commit

@app.route('/to-do-list', methods=['POST'])
@login_required 
def record_activity():
    user = current_user
    update_streak(user)
    return render_template('to_do_list.html', streak_record=user.streak_record)

