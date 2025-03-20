from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

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
    flash("Sign in first!", "error")  # Запазва съобщението в session
    return redirect(url_for("auth.login"))  # Пренасочване към login