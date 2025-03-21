from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, DailyChallenges, SleepTime
from . import db
from datetime import datetime
from .streak_counter import update_streak
from .sleeptime import get_sleep_duration
from flask import jsonify

views = Blueprint('views', __name__)

@views.route("/")
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    return render_template("welcome.html", user=current_user)


@views.route('/home')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@views.route('/redirect_to_profile')
def redirect_to_profile():
    flash("Sign in first!", "error") 
    return redirect(url_for("auth.login"))  

@views.route('/to-do-list', methods=['GET', 'POST'])
@login_required
def to_do_list():
    if request.method == 'POST':
        if request.is_json:
            meditation_data = request.get_json()
            task_text = meditation_data.get('task_data')  
            meditation_completed = meditation_data.get('completed')  
            if task_text:
                meditation_note = Note(data=task_text, user_id=current_user.id, completed=meditation_completed)
                db.session.add(meditation_note)
                db.session.commit()
        else:
            note_text = request.form.get('note')
            if note_text:
                new_note = Note(data=note_text, user_id=current_user.id, completed=False)
                db.session.add(new_note)
                db.session.commit()
    return render_template("to_do_list.html", user=current_user)

@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:  
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted!', category='success')
    else:
        flash('Note not found or unauthorized action.', category='error')
    return redirect(url_for('views.to_do_list'))

@views.route('/update-note/<int:note_id>', methods=['POST'])
@login_required
def update_note(note_id):
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id: 
        if not note.completed:  
            note.completed = True
            db.session.commit()
            flash('Task marked as completed!', category='success')
        else:
            flash('Completed tasks cannot be undone.', category='error')
    else:
        flash('Task not found or unauthorized action.', category='error')
    return redirect(url_for('views.to_do_list'))

@views.route('/meditation', methods=['GET', 'POST'])
@login_required
def meditation():
    return render_template("meditation.html", user=current_user)

@views.route('/sleep/log', methods=['POST', 'GET'])
def log_sleep():
    if request.method == 'POST':
        sleeptime_from = request.form.get('sleeptime_from')
        sleeptime_to = request.form.get('sleeptime_to')

        if not sleeptime_from or not sleeptime_to:
            flash('Please fill in both the start and end time for your sleep.', 'warning')
            return redirect(url_for('views.log_sleep'))

        try:
            sleeptime_from = datetime.strptime(sleeptime_from, '%Y-%m-%dT%H:%M')
            sleeptime_to = datetime.strptime(sleeptime_to, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format. Please make sure you select valid date and time.', 'danger')
            return redirect(url_for('views.log_sleep'))

        if sleeptime_from >= sleeptime_to:
            flash('Sleep start time cannot be later than or the same as the end time.', 'danger')
            return redirect(url_for('views.log_sleep'))

        new_sleep = SleepTime(user_id=current_user.id, sleeptime_from=sleeptime_from, sleeptime_to=sleeptime_to)

        try:
            db.session.add(new_sleep)
            db.session.commit()
            flash('Sleep time logged successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred while logging sleep: {e}', 'danger')

        return redirect(url_for('views.log_sleep'))

    return render_template('sleep.html', user=current_user)

@views.route('/sleep/delete/<int:sleep_id>', methods=['POST'])
def delete_sleep(sleep_id):
    sleep_entry = SleepTime.query.get(sleep_id)
    if sleep_entry:
        db.session.delete(sleep_entry)
        db.session.commit()
    return redirect(url_for('views.sleep'))

