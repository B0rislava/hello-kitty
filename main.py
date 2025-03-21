from website import create_app, db
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from website.models import Question, Answer, UserAnswer, User
from website.add_questions import init_questions

app = create_app()

@app.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def show_questions():
    if request.method == 'POST':
        # Изтриване на предишни отговори на текущия потребител
        UserAnswer.query.filter_by(user_id=current_user.id).delete()

        # Обработка на отговорите от формата
        for question in Question.query.all():
            answer_id = request.form.get(f'question_{question.id}')
            if answer_id:
                user_answer = UserAnswer(user_id=current_user.id, answer_id=int(answer_id))
                db.session.add(user_answer)
        
        db.session.commit()
        flash("Вашите отговори са записани!", "success")
        return redirect(url_for('show_questions'))  # Пренасочване след успешното записване

    # Извличане на всички въпроси от базата данни
    questions = Question.query.all()
    return render_template('questionnaire.html', questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
    init_questions()  # Инициализация на въпросите в базата данни
