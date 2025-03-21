from flask import Blueprint, render_template, request, flash, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from .models import Note, DailyChallenges, SleepTime
from werkzeug.security import generate_password_hash
from . import db
from datetime import datetime
from .streak_counter import update_streak
from .sleeptime import get_sleep_duration

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
    # Ако потребителят изпрати форма
    if request.method == 'POST':
        # Запазваме избора на аксесоари по категории
        hair_accessory = request.form.get('hair_accessory')
        clothing = request.form.get('clothing')
        jewelry = request.form.get('jewelry')

        # Запазваме в сесията
        session['hair_accessory'] = hair_accessory
        session['clothing'] = clothing
        session['jewelry'] = jewelry

        return redirect(url_for('views.profile'))

    # Извличаме стойности от сесията за аксесоарите
    hair_accessory = session.get('hair_accessory', '')
    clothing = session.get('clothing', '')
    jewelry = session.get('jewelry', '')

    # Извличаме стойности от базата данни за потребителя
    introvert = current_user.introvert or 3
    analytical = current_user.analytical or 3
    loyal = current_user.loyal or 3
    passive = current_user.passive or 3

    return render_template(
        "profile.html",
        user=current_user,
        introvert=introvert,
        analytical=analytical,
        loyal=loyal,
        passive=passive,
        hair_accessory=hair_accessory,
        clothing=clothing,
        jewelry=jewelry
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
        # Вземи продължителността на съня за текущия потребител
        sleeptime_from = request.form.get('sleeptime_from')
        sleeptime_to = request.form.get('sleeptime_to')

        if sleeptime_from and sleeptime_to:
            sleep_from = datetime.strptime(sleeptime_from, '%Y-%m-%dT%H:%M')
            sleep_to = datetime.strptime(sleeptime_to, '%Y-%m-%dT%H:%M')

            sleep_duration = sleep_to - sleep_from

            # Записваме продължителността в сесията
            session['sleep_duration'] = int(sleep_duration.total_seconds() // 3600)

            flash('Sleep logged successfully!', 'success')
            return redirect(url_for('views.home'))
        else:
            flash('Please provide both start and end time for your sleep!', 'error')

    return render_template('sleep.html')


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
    mood = data.get('mood', 'happy') 
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
