from flask import Blueprint, render_template
from flask_login import login_required, current_user

from website.forms import QuestionnaireForm

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/questionnaire', methods=['GET', 'POST'])
def index():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        answers = [form[f'question_{i}'].data for i in range(1, 24)]  # От 1 до 23

        return render_template('result.html', answers=answers)  # Показва резултата
    return render_template('questionnaire.html', form=form)
