from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.String(10), default=None)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(username=username)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created', 'username': username})

@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.json
    description = data.get('description')
    user_id = data.get('user_id')

    task = Task(description=description, user_id=user_id)
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created', 'description': description}), 201

@app.route('/complete_task', methods=['POST'])
def complete_task():
    data = request.json
    user_id = data.get('user_id')
    task_id = data.get('task_id')

    task = Task.query.filter_by(id=task_id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.completed = True
    db.session.commit()

    user = User.query.filter_by(id=user_id).first()
    if user:
        tasks = Task.query.filter_by(user_id=user_id).all()
        if all(task.completed for task in tasks):
            user.streak += 1 
            db.session.commit()

    return jsonify({'message': 'Task completed and streak updated', 'streak': user.streak}), 200

@app.route('/streak/<username>', methods=['GET'])
def get_streak(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'username': username, 'streak': user.streak}), 200

if __name__ == '__main__':
    app.run(debug=True)
