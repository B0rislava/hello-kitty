from flask import Blueprint, render_template, request, flash, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash

from .models import Note
from . import db
from datetime import datetime, timedelta
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
    if request.method == 'POST':
        accessory = request.form.get('accessory')
        session['accessory'] = accessory
        return redirect(url_for('views.profile'))

    return render_template("profile.html", user=current_user)



@views.route('/redirect_to_profile')
def redirect_to_profile():
    flash("Sign in first!", "error")
    return redirect(url_for("auth.login"))

@views.route('/to-do-list', methods=['GET', 'POST'])
@login_required
def to_do_list():
    update_streak(current_user)

    if request.method == 'POST':
        note_data = request.form.get('note')
        if len(note_data.strip()) < 1:
            flash('Note cannot be empty!', category='error')
        else:
            new_note = Note(data=note_data, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
        return redirect(url_for('views.to_do_list'))

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

@views.route('/meditation')
def meditation():
    return render_template("meditation.html", user=current_user)

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