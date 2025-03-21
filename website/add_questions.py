from website import db
from website.models import Question, Answer
from website.data.questions import questions  # Import questions from the new file

# Add questions to the database

def init_questions():

    for question_text in questions:
        question = Question(text=question_text)
        db.session.add(question)
        db.session.commit()

    # db.session.commit()
    print("Questions added to the database!")

    # Проверка дали въпросите и отговорите са в базата данни
    questions = Question.query.all()

    if len(questions) == 0:
        print("Няма въпроси в базата данни!")
    else:
        print(f"Има {len(questions)} въпроса в базата данни.")

        # Проверка дали въпросите имат отговори
        for question in questions:
            answers = Answer.query.filter_by(question_id=question.id).all()
            if len(answers) == 0:
                print(f"Въпросът '{question.text}' няма отговори.")
            else:
                print(f"Въпросът '{question.text}' има {len(answers)} отговора.")
