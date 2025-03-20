from flask import Blueprint, render_template, request, flash, redirect, url_for, flash
from flask_login import login_required, current_user
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