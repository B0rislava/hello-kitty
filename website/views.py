from flask import Blueprint, render_template, request, flash, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from .models import Note, DailyChallenges, SleepTime
from werkzeug.security import generate_password_hash
from . import db
from datetime import datetime
from .streak_counter import update_streak

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

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # If the user submits a form (e.g., accessory customization)
    if request.method == 'POST':
        accessory = request.form.get('accessory')
        session['accessory'] = accessory
        return redirect(url_for('views.profile'))

    # Fetch survey results from the database for the current user
    introvert = current_user.introvert or 3  # Default to 3 if no value is set
    analytical = current_user.analytical or 3
    loyal = current_user.loyal or 3
    passive = current_user.passive or 3
    accessory = session.get('accessory', '')

    # Render the profile page with the fetched values
    return render_template(
        "profile.html",
        user=current_user,
        introvert=introvert,
        analytical=analytical,
        loyal=loyal,
        passive=passive,
        accessory=accessory
    )


@views.route('/redirect_to_profile')
def redirect_to_profile():
    flash("Sign in first!", "error")
    return redirect(url_for("auth.login"))

@views.route('/to-do-list', methods=['GET', 'POST'])
@login_required
def to_do_list():
    update_streak(current_user)

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

@views.route('/articles')
def articles():
    return render_template('articles.html', user=current_user)


@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_name = request.form.get('first_name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')

        if new_name:
            current_user.first_name = new_name
        if new_email:
            current_user.email = new_email

        if new_password:
            if len(new_password) >= 8:
                current_user.password = generate_password_hash(new_password)
            else:
                flash("Password must be at least 8 characters long.", "error")
                return redirect(url_for('views.edit_profile'))

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('views.profile'))

    return render_template('edit_profile.html', user=current_user)

@views.route('/update_accessory', methods=['POST'])
@login_required
def update_accessory():
    data = request.get_json()
    accessory = data.get('accessory')

    if accessory == 'none':
        session.pop('accessory', None)
    else:
        session['accessory'] = accessory

    return jsonify({'accessory': session.get('accessory')})


@views.route('/update_mood', methods=['POST'])
def update_mood():
    data = request.get_json()
    mood = data.get('mood', 'happy')  # Default mood is 'happy'
    session['mood'] = mood
    return jsonify({'mood': mood})




@views.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    if request.method == 'POST':
   
        introvert_score = int(request.form['introvert'])
        analytical_score = int(request.form['analytical'])
        loyal_score = int(request.form['loyal'])
        passive_score = int(request.form['passive'])

        user = current_user
        user.introvert = introvert_score
        user.analytical = analytical_score
        user.loyal = loyal_score
        user.passive = passive_score
        db.session.commit()

        return redirect(url_for('views.profile'))

    return render_template('survey.html')
