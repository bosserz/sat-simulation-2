# sat_bluebook_app/models.py

from app import db # Import the db instance from your app.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to store user test attempts
    test_attempts = db.relationship('UserTestAttempt', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    # Relationship to questions (e.g., a topic can have many questions)
    questions = db.relationship('Question', backref='topic', lazy='dynamic')

    def __repr__(self):
        return f'<Topic {self.name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False) # e.g., 'multiple_choice', 'grid_in'
    # An image path could be added here if questions have images
    # image_path = db.Column(db.String(256))

    # Foreign key to Topic
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True) # A question can optionally belong to a topic

    # Relationships for choices and correct answer
    choices = db.relationship('Choice', backref='question', lazy='dynamic', cascade="all, delete-orphan")
    # For multiple choice, this points to the correct choice's ID
    # For grid-in, this could store the correct numeric answer as text or another field
    correct_answer_id = db.Column(db.Integer, db.ForeignKey('choice.id'), nullable=True)
    correct_grid_in_answer = db.Column(db.String(128), nullable=True) # For grid-in questions

    explanation = db.Column(db.Text, nullable=True) # Explanation for the answer

    def __repr__(self):
        return f'<Question {self.id}>'

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f'<Choice {self.id}: {self.text[:20]}...>'


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Many-to-Many relationship for Test and Question
    # This table links which questions belong to which test
    questions = db.relationship('Question', secondary='test_question', backref='tests', lazy='dynamic')

    def __repr__(self):
        return f'<Test {self.name}>'

# Association table for the many-to-many relationship between Test and Question
test_question = db.Table('test_question',
    db.Column('test_id', db.Integer, db.ForeignKey('test.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)

class UserTestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    score = db.Column(db.Integer, nullable=True) # Raw score, not scaled SAT score
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    attempt_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Store answers as JSON string (or a separate table for more complex tracking)
    # Example: {"question_id_1": "choice_id_A", "question_id_2": "grid_in_value"}
    answers_json = db.Column(db.Text, nullable=True)

    test = db.relationship('Test', backref='attempts', lazy=True)

    def __repr__(self):
        return f'<UserTestAttempt User:{self.user_id} Test:{self.test_id} Score:{self.score}>'
    
    