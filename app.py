from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime, timedelta
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sat_practice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session lasts 1 day
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Admin access: comma-separated usernames in env var, or hardcode here
ADMIN_USERNAMES = set(
    u.strip() for u in os.environ.get("ADMIN_USERNAMES", "admin").split(",") if u.strip()
)

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL is None:
    DATABASE_URL = "sqlite:///sat_practice.db"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Set SQLAlchemy configuration
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///sat_practice.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if DATABASE_URL and "postgresql" in DATABASE_URL:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"sslmode": "require"}}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Models
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class TestSession(db.Model):
    __tablename__ = "test_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    practice_test_id = db.Column(db.String(10), nullable=False)  # ID of the practice test (e.g., 'test1', 'test2')
    start_time = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Integer, nullable=True)
    answers = db.Column(db.Text, nullable=True)  # JSON string of answers
    current_question = db.Column(db.Integer, default=0)
    current_section = db.Column(db.Integer, default=0)  # 0 to 3 for the 4 sections
    marked_for_review = db.Column(db.Text, nullable=True)  # JSON string of marked questions
    section_start_time = db.Column(db.DateTime, nullable=True)


class TextHighlight(db.Model):
    __tablename__ = "text_highlights"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    test_session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'), nullable=False, index=True)
    section_idx = db.Column(db.Integer, nullable=False, index=True)
    question_idx = db.Column(db.Integer, nullable=False, index=True)
    target = db.Column(db.String(20), nullable=False, default='passage')
    start_offset = db.Column(db.Integer, nullable=False)
    end_offset = db.Column(db.Integer, nullable=False)
    selected_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "section_idx": self.section_idx,
            "question_idx": self.question_idx,
            "target": self.target,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "selected_text": self.selected_text,
        }


class DrillSet(db.Model):
    __tablename__ = "drill_sets"
    
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False, index=True)  # e.g., "Words in Context"
    skill_name = db.Column(db.String(100), nullable=False)  # Same as topic for now
    section_type = db.Column(db.String(20), nullable=False)  # 'verbal' or 'math'
    set_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3...
    difficulty = db.Column(db.String(20), nullable=False)  # 'Easy', 'Medium', 'Hard'
    num_questions = db.Column(db.Integer, nullable=False)
    question_ids = db.Column(db.Text, nullable=False)  # JSON array of question IDs
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('ix_drill_topic_difficulty', 'topic_name', 'difficulty'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'skill_name': self.skill_name,
            'section_type': self.section_type,
            'set_number': self.set_number,
            'difficulty': self.difficulty,
            'num_questions': self.num_questions,
            'question_ids': json.loads(self.question_ids),
            'description': self.description,
        }


class DrillSession(db.Model):
    __tablename__ = "drill_sessions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    drill_set_id = db.Column(db.Integer, db.ForeignKey('drill_sets.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)  # Time taken in seconds
    answers = db.Column(db.Text, nullable=False)  # JSON: {question_id: user_answer}
    correct_count = db.Column(db.Integer)  # Number of correct answers
    total_count = db.Column(db.Integer)  # Total questions
    accuracy_percent = db.Column(db.Float)  # 0-100
    use_timer = db.Column(db.Boolean, default=False)  # Did user enable timer?
    
    drill_set = db.relationship('DrillSet', backref='sessions')
    user = db.relationship('User', backref='drill_sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'drill_set_id': self.drill_set_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'correct_count': self.correct_count,
            'total_count': self.total_count,
            'accuracy_percent': self.accuracy_percent,
            'use_timer': self.use_timer,
        }


class DrillSetProgress(db.Model):
    __tablename__ = "drill_set_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    topic_name = db.Column(db.String(100), nullable=False, index=True)
    total_attempts = db.Column(db.Integer, default=0)
    completed_sets = db.Column(db.Integer, default=0)  # e.g., 2/3 sets
    best_score = db.Column(db.Float)  # Best accuracy across all attempts
    last_attempt_date = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='drill_progress')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'topic_name', name='uq_user_topic'),
        db.Index('ix_user_progress', 'user_id', 'topic_name'),
    )

# Load questions
with open('database/questions.json', 'r') as f:
    ALL_QUESTIONS = json.load(f)

# Section configuration
SECTIONS = [
    {"name": "Section 1: Verbal - Module 1", "type": "verbal", "module": 1, "duration": 1920},  # 32 minutes
    {"name": "Section 2: Verbal - Module 2", "type": "verbal", "module": 2, "duration": 1920},  # 32 minutes
    {"name": "Section 3: Math - Module 1", "type": "math", "module": 1, "duration": 2100},    # 35 minutes
    {"name": "Section 4: Math - Module 2", "type": "math", "module": 2, "duration": 2100},    # 35 minutes
]

# Filter questions for a given section and practice test
def get_questions_for_section(section_idx, practice_test_id):
    section = SECTIONS[section_idx]
    practice_test_questions = ALL_QUESTIONS.get(practice_test_id, [])
    return [
        q for q in practice_test_questions
        if q['type'] == section['type'] and q['module'] == section['module']
    ]


# Initialize drill sets from questions.json
def initialize_drill_sets():
    """Populate DrillSet table from the drill_sets in questions.json"""
    drill_sets_data = ALL_QUESTIONS.get('drill_sets', {})
    
    for topic_name, topic_data in drill_sets_data.items():
        section_type = topic_data.get('section_type', 'verbal')
        skill_name = topic_name  # For now, skill_name = topic_name
        description = topic_data.get('description', '')
        
        sets_data = topic_data.get('sets', {})
        
        for set_key, set_info in sets_data.items():
            set_number = int(set_key.split('_')[1])  # Extract number from set_1, set_2, etc.
            difficulty = set_info.get('difficulty', 'Medium')
            num_questions = set_info.get('num_questions', 0)
            question_ids = set_info.get('question_ids', [])
            
            # Check if this drill set already exists
            existing = DrillSet.query.filter_by(
                topic_name=topic_name,
                set_number=set_number,
                difficulty=difficulty
            ).first()
            
            if not existing:
                drill_set = DrillSet(
                    topic_name=topic_name,
                    skill_name=skill_name,
                    section_type=section_type,
                    set_number=set_number,
                    difficulty=difficulty,
                    num_questions=num_questions,
                    question_ids=json.dumps(question_ids),
                    description=description
                )
                db.session.add(drill_set)
    
    try:
        db.session.commit()
        print(f"✅ Initialized drill sets in database")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Error initializing drill sets: {e}")


# Get all available drill topics with metadata
def get_drill_topics():
    """Return list of all drill topics grouped by section type"""
    drill_sets_data = ALL_QUESTIONS.get('drill_sets', {})
    
    topics_by_section = {'verbal': [], 'math': []}
    
    for topic_name, topic_data in drill_sets_data.items():
        section_type = topic_data.get('section_type', 'verbal')
        description = topic_data.get('description', '')
        sets_data = topic_data.get('sets', {})
        num_sets = len(sets_data)
        
        # Get user's progress on this topic
        user_id = session.get('user_id')
        progress = None
        if user_id:
            progress = DrillSetProgress.query.filter_by(
                user_id=user_id,
                topic_name=topic_name
            ).first()
        
        topic_info = {
            'topic_name': topic_name,
            'description': description,
            'section_type': section_type,
            'num_sets': num_sets,
            'completed_sets': progress.completed_sets if progress else 0,
            'best_score': progress.best_score if progress else None,
            'last_attempt_date': progress.last_attempt_date if progress else None,
        }
        
        topics_by_section[section_type].append(topic_info)
    
    return topics_by_section


# Get sets for a specific topic
def get_drill_sets_for_topic(topic_name):
    """Return all drill sets for a given topic with user's history"""
    return DrillSet.query.filter_by(topic_name=topic_name).order_by(
        DrillSet.difficulty,
        DrillSet.set_number
    ).all()


# Get skill questions by IDs
def get_skill_questions(question_ids):
    """Get question objects from skill_questions array by IDs"""
    skill_questions = ALL_QUESTIONS.get('skill_questions', [])
    questions = [q for q in skill_questions if q['question_id'] in question_ids]
    return questions


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_test', methods=['GET', 'POST'])
def select_test():
    incomplete_session = TestSession.query.filter_by(user_id=session['user_id'], score=None).first()
    if incomplete_session:
        flash('Please complete your ongoing test before starting a new one.')
        return redirect(url_for('dashboard'))
    
    if 'user_id' not in session:
        flash('Please log in to select a practice test.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        practice_test_id = request.form.get('practice_test_id')
        if practice_test_id not in ALL_QUESTIONS:
            flash('Invalid practice test selected.')
            return redirect(url_for('select_test'))
        
        session['new_test'] = True
        session['practice_test_id'] = practice_test_id
        return redirect(url_for('practice'))
    
    # List available practice tests
    practice_tests = list(ALL_QUESTIONS.keys())
    # result = supabase.table("questions").select("test").execute()
    # practice_tests = sorted(set(q["test"] for q in result.data))

    return render_template('select_test.html', practice_tests=practice_tests)

# @app.route('/select_test', methods=['GET', 'POST'])
# def select_test():
#     if 'user_id' not in session:
#         flash('Please log in to select a practice test.')
#         return redirect(url_for('login'))

#     incomplete_session = TestSession.query.filter_by(user_id=session['user_id'], score=None).first()
#     if incomplete_session:
#         flash('Please complete your ongoing test before starting a new one.')
#         return redirect(url_for('dashboard'))

#     if request.method == 'POST':
#         practice_test_id = request.form.get('practice_test_id')

#         # ✅ Check if the test exists in Supabase
#         result = supabase.table("questions") \
#             .select("id") \
#             .eq("test", practice_test_id) \
#             .limit(1) \
#             .execute()

#         if not result.data:
#             flash('Invalid practice test selected.')
#             return redirect(url_for('select_test'))

#         session['new_test'] = True
#         session['practice_test_id'] = practice_test_id
#         return redirect(url_for('practice'))

#     # ✅ Load list of available test sets from Supabase
#     result = supabase.table("questions").select("test").execute()
#     if not result.data:
#         flash('Unable to load practice tests.')
#         return redirect(url_for('dashboard'))

#     practice_tests = sorted(set(q["test"] for q in result.data))
#     return render_template('select_test.html', practice_tests=practice_tests)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/request_account', methods=['GET'])
def request_account():
    
    return render_template('request_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True  # Make session permanent
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('test_session_id', None)  # Clear test session
    session.pop('practice_test_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    # Get most recent incomplete session (score is None)
    active_session = TestSession.query.filter_by(
        user_id=user.id, score=None
    ).order_by(TestSession.start_time.desc()).first()

    test_sessions = TestSession.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', 
                           username=session['username'], 
                           test_sessions=test_sessions,
        active_session=active_session)

@app.route('/resume_test', methods=['POST'])
def resume_test():
    if 'user_id' not in session:
        flash('Please log in to resume a test.')
        return redirect(url_for('login'))

    session_id = request.form.get('session_id')
    test_session = TestSession.query.get(session_id)

    if not test_session or test_session.user_id != session['user_id'] or test_session.score is not None:
        flash('Invalid or completed test session.')
        return redirect(url_for('dashboard'))

    # Restore session state
    session['test_session_id'] = test_session.id
    session['practice_test_id'] = test_session.practice_test_id
    session['new_test'] = False  # Ensure it's marked as a continuation

    return redirect(url_for('practice'))

@app.route('/get_remaining_time')
def get_remaining_time():
    if 'user_id' not in session or 'test_session_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    test_session = TestSession.query.get(session['test_session_id'])
    if not test_session:
        return jsonify({'error': 'Session not found'}), 404

    section_duration = SECTIONS[test_session.current_section]['duration']
    if test_session.section_start_time:
        elapsed = (datetime.utcnow() - test_session.section_start_time).total_seconds()
    else:
        elapsed = 0
        test_session.section_start_time = datetime.utcnow()
        db.session.commit()

    remaining = max(0, int(section_duration - elapsed))
    return jsonify({'remaining_time': remaining})


@app.route('/practice', methods=['GET', 'POST'])
def practice():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in to start practicing.'}), 401
    
    if 'practice_test_id' not in session:
        flash('Please select a practice test.')
        return redirect(url_for('select_test'))
    
    practice_test_id = session['practice_test_id']
    
    # Create a new test session if none exists or if the last one is completed
    # test_session = TestSession.query.filter_by(user_id=session['user_id']).order_by(TestSession.start_time.desc()).first()
    test_session = None
    if 'test_session_id' in session:
        test_session = TestSession.query.get(session['test_session_id'])

    if not test_session or test_session.user_id != session['user_id']:
        # fallback to latest
        test_session = TestSession.query.filter_by(user_id=session['user_id']).order_by(TestSession.start_time.desc()).first()

    if not test_session or test_session.score is not None or test_session.practice_test_id != practice_test_id:
        test_session = TestSession(
            user_id=session['user_id'],
            practice_test_id=practice_test_id,
            start_time=datetime.utcnow(),
            section_start_time=datetime.utcnow(),
            answers=json.dumps({}),
            marked_for_review=json.dumps({}),
            current_section=0,  # Reset to first section
            current_question=0  # Reset to first question
        )
        db.session.add(test_session)
        db.session.commit()
    else:
        # Reset current_section and current_question if starting anew
        if 'new_test' in session and session['new_test']:
            test_session.current_section = 0
            test_session.current_question = 0
            test_session.answers = json.dumps({})
            test_session.marked_for_review = json.dumps({})
            test_session.score = None
            db.session.commit()
            session.pop('new_test', None)
    
    session['test_session_id'] = test_session.id
    session['new_test'] = False  # Reset the flag
    
    if request.method == 'POST':
        data = request.json
        print(f"POST data received: {data}")  # Debugging
        answers = json.loads(test_session.answers)
        marked = json.loads(test_session.marked_for_review)
        
        # Compute answer_key for both answers and mark_for_review
        qid = str(data.get('current_question'))
        answer_key = f"{test_session.current_section}_{qid}"
        
        # Update answers
        answer = data.get('answer')
        if answer:
            answers[answer_key] = answer
        
        # Update marked for review
        if data.get('mark_for_review') is not None:
            marked[answer_key] = data.get('mark_for_review')
        
        # Update current question
        next_question = data.get('next_question')
        if next_question is not None:
            test_session.current_question = next_question
            section_questions = get_questions_for_section(test_session.current_section, practice_test_id)
            if next_question >= len(section_questions):
                # End of section
                if test_session.current_section < len(SECTIONS) - 1:
                    # Move to break page
                    test_session.current_question = 0
                    test_session.current_section += 1
                    # test_session.section_start_time = datetime.utcnow()
                    test_session.section_start_time = None
                    test_session.answers = json.dumps(answers)
                    test_session.marked_for_review = json.dumps(marked)
                    db.session.commit()
                    return jsonify({'redirect': url_for('break_page')})
                else:
                    # End of test, calculate score
                    score = 0
                    section_scores = {}
                    for section_idx in range(len(SECTIONS)):
                        section_questions = get_questions_for_section(section_idx, practice_test_id)
                        section_score = 0
                        for qid in range(len(section_questions)):
                            answer_key = f"{section_idx}_{qid}"
                            ans = answers.get(answer_key)
                            if ans and section_questions[qid]['correct_answer'] == ans:
                                section_score += 1
                        section_scores[section_idx] = section_score
                        score += section_score
                    test_session.score = score
                    test_session.answers = json.dumps(answers)
                    test_session.marked_for_review = json.dumps(marked)
                    db.session.commit()
                    print(f"Test completed. Score: {score}, Redirecting to results.")  # Debugging
                    return jsonify({'redirect': url_for('results', session_id=test_session.id)})
        
        test_session.answers = json.dumps(answers)
        test_session.marked_for_review = json.dumps(marked)
        db.session.commit()
        
        # Return the next question
        current_question = test_session.current_question
        section_questions = get_questions_for_section(test_session.current_section, practice_test_id)
        # section_questions = session.get('current_section_questions', [])
        question = section_questions[current_question]
        response = {
            'question': question,
            'qid': current_question,
            'section_idx': test_session.current_section,
            'test_session_id': test_session.id,
            'answer': answers.get(f"{test_session.current_section}_{current_question}", ''),
            'marked': marked.get(f"{test_session.current_section}_{current_question}", False),
            'total_questions': len(section_questions),
            'section_name': SECTIONS[test_session.current_section]['name']
        }
        print(f"Returning question data: {response}")  # Debugging
        return jsonify(response)
    
    section_duration = SECTIONS[test_session.current_section]['duration']

    # if test_session.section_start_time:
    #     elapsed = (datetime.utcnow() - test_session.section_start_time).total_seconds()
    # else:
    #     # In case section_start_time was never set
    #     test_session.section_start_time = datetime.utcnow()
    #     db.session.commit()
    #     elapsed = 0

    # remaining_time = max(0, section_duration - int(elapsed))

    if test_session.section_start_time:
        elapsed = (datetime.utcnow() - test_session.section_start_time).total_seconds()
        remaining_time = max(0, section_duration - int(elapsed))
    else:
        # Not started yet → show full time but DO NOT start
        remaining_time = section_duration


    return render_template('practice.html', test_duration=remaining_time)
    # return render_template('practice.html', test_duration=SECTIONS[test_session.current_section]['duration'])

@app.route('/break')
def break_page():
    if 'user_id' not in session or 'test_session_id' not in session:
        flash('Please start a practice test.')
        return redirect(url_for('dashboard'))
    
    test_session = TestSession.query.get(session['test_session_id'])
    if test_session.score is not None:
        return redirect(url_for('results', session_id=test_session.id))
    
    session['new_test'] = False  # Ensure new_test flag is reset
    return render_template('break.html', next_section=SECTIONS[test_session.current_section]['name'])

# Full Results
@app.route('/get_full_results/<int:session_id>')
def get_full_results(session_id):
    if 'user_id' not in session:
        flash('Please log in to view results.')
        return redirect(url_for('login'))
    
    test_session = TestSession.query.get_or_404(session_id)
    if test_session.user_id != session['user_id']:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))
    
    practice_test_id = test_session.practice_test_id
    answers = json.loads(test_session.answers)
    marked = json.loads(test_session.marked_for_review)
    
    # Calculate section scores
    section_scores = {}
    section_answers = {}
    for section_idx in range(len(SECTIONS)):
        section_questions = get_questions_for_section(section_idx, practice_test_id)
        section_score = 0
        section_ans = {}
        for qid in range(len(section_questions)):
            answer_key = f"{section_idx}_{qid}"
            ans = answers.get(answer_key)
            if ans and section_questions[qid]['correct_answer'] == ans:
                section_score += 1
            section_ans[qid] = {
                'answer': ans,
                'marked': marked.get(answer_key, False)
            }
        section_scores[section_idx] = section_score
        section_answers[section_idx] = section_ans

    # result = supabase.table("questions").select("*").eq("test", practice_test_id).order("id").execute()
    # questions = result.data
    
    return render_template(
        'results.html',
        score=test_session.score,
        section_scores=section_scores,
        section_answers=section_answers,
        sections=SECTIONS,
        questions=ALL_QUESTIONS[practice_test_id]
    )

from collections import defaultdict

# def build_domain_stats(sections, questions, section_answers, practice_test_id):
#     """
#     Returns:
#       {
#         'verbal': {'Craft and Structure': {'correct': 5, 'total': 7}, ...},
#         'math':   {'Algebra': {'correct': 3, 'total': 5}, ...}
#       }
#     """
#     # Map: (type, module) -> list of its questions (in display order)
#     sect_qs = {}
#     for s in sections:
#         key = (s['type'].lower(), s.get('module'))
#         qs = [q for q in questions[practice_test_id] if q['type'].lower() == s['type'].lower() and q.get('module') == s.get('module')]
#         sect_qs[key] = qs

#     # Tally per section-type per domain
#     domain_stats = {
#         'verbal': defaultdict(lambda: {'correct': 0, 'total': 0}),
#         'math':   defaultdict(lambda: {'correct': 0, 'total': 0}),
#     }

#     # Iterate sections in order so answers align: section_answers[i][qid]
#     for i, s in enumerate(sections):
#         s_type = s['type'].lower()
#         key = (s_type, s.get('module'))
#         qs = sect_qs.get(key, [])
#         answers_i = section_answers[i] if i < len(section_answers) else []

#         for qid, q in enumerate(qs):
#             dom = q.get('domain', 'Other')
#             domain_stats[s_type][dom]['total'] += 1

#             ans = None
#             if qid < len(answers_i):
#                 ans = answers_i[qid].get('answer')
#             if ans is not None and ans == q.get('correct_answer'):
#                 domain_stats[s_type][dom]['correct'] += 1

#     # Convert defaultdicts to normal dicts
#     for k in ('verbal', 'math'):
#         domain_stats[k] = dict(domain_stats[k])

#     return domain_stats

# Calculate Score
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any, Union, Iterable, Dict

LEVEL_POINTS = {"Easy": 9, "Medium": 10, "Hard": 12}

def _normalize_numeric(val: Any) -> Decimal | None:
    """Return Decimal rounded to 4 dp (half up) from string/number like '1/3' or '0.3333'.
    Returns None if not parseable."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        if "/" in s:
            # fraction a/b
            num, den = s.split("/", 1)
            dnum = Decimal(num.strip())
            dden = Decimal(den.strip())
            if dden == 0:
                return None
            value = dnum / dden
        else:
            value = Decimal(s)
        return value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, ZeroDivisionError):
        return None

def _is_fill_in_math(q: Dict) -> bool:
    """Heuristics: math + no options OR explicit flags."""
    qtype = (q.get("type") or "").lower()
    if qtype != "math":
        return False
    # explicit flags (use any your data may have)
    if q.get("format") in {"fitb", "fill", "numeric"} or q.get("answer_type") in {"numeric", "number"}:
        return True
    # heuristic: no choices -> fill-in
    opts = q.get("options")
    return opts in (None, [], "")

def _match_answer(q: Dict, user_ans: Any) -> bool:
    """Returns True if user answer is correct per rules."""
    if user_ans is None:
        return False

    corr = q.get("correct_answer")

    # If correct answers is a list -> any correct counts
    corr_list: Iterable = corr if isinstance(corr, (list, tuple, set)) else [corr]

    if _is_fill_in_math(q):
        # numeric compare at 4 dp
        u = _normalize_numeric(user_ans)
        if u is None:
            return False
        for c in corr_list:
            c_norm = _normalize_numeric(c)
            if c_norm is not None and c_norm == u:
                return True
        return False
    else:
        # string/choice compare (case-sensitive by default; tweak if needed)
        u = str(user_ans).strip()
        for c in corr_list:
            if str(c).strip() == u:
                return True
        return False
    
def build_domain_chart_data(sections, questions, section_answers) -> Dict[str, Dict[str, list]]:
    """
    Returns structure ready for Chart.js with *no* frontend math:
    {
      'verbal': {
        'labels': [...],
        'correct': [...],
        'incorrect': [...],
        'totals': [...],
        'pct_correct': [...],   # integers 0..100
        'pct_incorrect': [...]
      },
      'math': { ... }
    }
    """
    # Pre-index questions by (type,module) preserving order
    by_tm: Dict[tuple, list] = {}
    for s in sections:
        key = (s["type"].lower(), s.get("module"))
        if key not in by_tm:
            by_tm[key] = [q for q in questions
                          if (q.get("type","").lower() == key[0]) and (q.get("module") == key[1])]

    # Accumulators per section-type per domain
    tallies = {
        "verbal": defaultdict(lambda: {"correct": 0, "total": 0}),
        "math":   defaultdict(lambda: {"correct": 0, "total": 0}),
    }

    # Iterate sections in given order so answers align (section_answers[i][qid])
    for i, s in enumerate(sections):
        stype = s["type"].lower()
        smod = s.get("module")
        qs = by_tm.get((stype, smod), [])
        ans_list = section_answers[i] if i < len(section_answers) else []

        for qid, q in enumerate(qs):
            dom = q.get("domain", "Other")
            tallies[stype][dom]["total"] += 1
            user_ans = ans_list[qid].get("answer") if qid < len(ans_list) else None
            if _match_answer(q, user_ans):
                tallies[stype][dom]["correct"] += 1

    # Convert to arrays (sorted by domain name) with percentages precomputed
    out: Dict[str, Dict[str, list]] = {}
    for stype in ("verbal", "math"):
        rows = []
        for dom, v in tallies[stype].items():
            total = v["total"]
            correct = v["correct"]
            incorrect = max(0, total - correct)
            pct_c = int(round(100 * correct / total)) if total else 0
            pct_i = 100 - pct_c if total else 0
            rows.append((dom, correct, incorrect, total, pct_c, pct_i))
        rows.sort(key=lambda r: r[0])  # sort by domain label

        out[stype] = {
            "labels":        [r[0] for r in rows],
            "correct":       [r[1] for r in rows],
            "incorrect":     [r[2] for r in rows],
            "totals":        [r[3] for r in rows],
            "pct_correct":   [r[4] for r in rows],
            "pct_incorrect": [r[5] for r in rows],
        }
    return out

def compute_section_scores(sections, questions, section_answers, module_multipliers=None):
    """
    Returns dict with raw/max per module, scaled per your caps, and rounded section/total.
    sections: list of dicts; each has type ('verbal'/'math') and module (1/2) in the same order as section_answers
    questions: flat list of question dicts
    section_answers: list aligned to sections: section_answers[i][qid]['answer']
    module_multipliers: {'verbal': {1:1.0,2:1.0}, 'math': {1:1.0,2:1.0}} (optional)
    """
    mm = module_multipliers or {}
    out = {
        "verbal": {"m1_raw": 0.0, "m1_max": 0.0, "m2_raw": 0.0, "m2_max": 0.0},
        "math":   {"m1_raw": 0.0, "m1_max": 0.0, "m2_raw": 0.0, "m2_max": 0.0},
    }

    # Index questions by (type,module) to preserve order
    by_tm: Dict[tuple, list] = {}
    for s in sections:
        key = (s["type"].lower(), s.get("module"))
        if key not in by_tm:
            by_tm[key] = [q for q in questions
                          if (q.get("type","").lower() == key[0]) and (q.get("module") == key[1])]

    for i, s in enumerate(sections):
        stype = s["type"].lower()
        smod = s.get("module")
        qs = by_tm.get((stype, smod), [])
        answers_i = section_answers[i] if i < len(section_answers) else []

        # pick multipliers map: prefer per-section, else flat
        per_sec_mm = (mm.get(stype) or {})
        for qid, q in enumerate(qs):
            base = LEVEL_POINTS.get(q.get("level"), 10)
            mult = per_sec_mm.get(q.get("module")) or mm.get(q.get("module"), 1.0) or 1.0
            # increase maximum
            if q.get("module") == 1:
                out[stype]["m1_max"] += base * mult
            elif q.get("module") == 2:
                out[stype]["m2_max"] += base * mult
            # user answer
            ans = answers_i[qid].get("answer") if qid < len(answers_i) else None
            if _match_answer(q, ans):
                if q.get("module") == 1:
                    out[stype]["m1_raw"] += base * mult
                elif q.get("module") == 2:
                    out[stype]["m2_raw"] += base * mult

    def _scaled(d):
        m1 = 0 if d["m1_max"] == 0 else 200 * (d["m1_raw"] / d["m1_max"])
        m2 = 0 if d["m2_max"] == 0 else 400 * (d["m2_raw"] / d["m2_max"])
        m1 = min(m1, 200)
        m2 = min(m2, 400)
        s = 200 + m1 + m2
        return max(200, min(800, round(s)))

    verbal_scaled = _scaled(out["verbal"])
    math_scaled   = _scaled(out["math"])

    # round sections to nearest 10
    def round10(x: Union[int, float]) -> int:
        return int(Decimal(x).quantize(Decimal("1E1"), rounding=ROUND_HALF_UP))
    verbal_10 = round10(verbal_scaled)
    math_10   = round10(math_scaled)
    total_10  = verbal_10 + math_10

    return {
        "per_section": out,
        "verbal_score": verbal_10,
        "math_score": math_10,
        "total_score": total_10,
    }


@app.route('/mock_results/<int:session_id>')
def results(session_id):
    if 'user_id' not in session:
        flash('Please log in to view results.')
        return redirect(url_for('login'))
    
    test_session = TestSession.query.get_or_404(session_id)
    if test_session.user_id != session['user_id']:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))
    
    practice_test_id = test_session.practice_test_id
    answers = json.loads(test_session.answers)
    marked = json.loads(test_session.marked_for_review)
    
    # Calculate section scores
    section_scores = {}
    section_answers = {}
    for section_idx in range(len(SECTIONS)):
        section_questions = get_questions_for_section(section_idx, practice_test_id)
        section_score = 0
        section_ans = {}
        for qid in range(len(section_questions)):
            answer_key = f"{section_idx}_{qid}"
            ans = answers.get(answer_key)
            if ans and section_questions[qid]['correct_answer'] == ans:
                section_score += 1
            section_ans[qid] = {
                'answer': ans,
                'marked': marked.get(answer_key, False)
            }
        section_scores[section_idx] = section_score
        section_answers[section_idx] = section_ans

    # result = supabase.table("questions").select("*").eq("test", practice_test_id).order("id").execute()
    # questions = result.data

    module_multipliers = {
        'verbal': {1: 1.0, 2: 1.66},
        'math':   {1: 0.79, 2: 1.345},
    }


    # domain_stats = build_domain_stats(SECTIONS, ALL_QUESTIONS, section_answers, practice_test_id)
    domain_chart_data = build_domain_chart_data(SECTIONS, ALL_QUESTIONS[practice_test_id], section_answers)

    scores = compute_section_scores(SECTIONS, ALL_QUESTIONS[practice_test_id], section_answers, module_multipliers)
    
    return render_template(
        'mock_results.html',
        verbal_score=scores["verbal_score"],
        math_score=scores["math_score"],
        total_score=scores["total_score"],
        # domain_stats=domain_stats
        domain_chart_data=domain_chart_data,
    )

# app.py
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from fractions import Fraction
from markupsafe import Markup, escape
import json, re
from html import unescape as html_unescape

# ---------- Numeric helpers ----------
def _new_normalize_numeric(val):
    if val is None:
        return None
    if isinstance(val, (int, float, Decimal)):
        try:
            d = Decimal(str(val))
            return d.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        except InvalidOperation:
            return None
    s = str(val).strip()
    if not s:
        return None
    if '/' in s:
        try:
            frac = Fraction(s)
            d = Decimal(frac.numerator) / Decimal(frac.denominator)
            return d.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        except Exception:
            pass
    try:
        d = Decimal(s)
        return d.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return None

def _equal_numeric(a, b):
    da, db = _new_normalize_numeric(a), _new_normalize_numeric(b)
    return (da is not None) and (db is not None) and (da == db)

# ---------- Text normalization (for MCQ string match) ----------
_TAG_RE = re.compile(r"<[^>]+>")

def _norm_text(x):
    s = str(x)
    s = html_unescape(s)
    s = _TAG_RE.sub("", s)           # strip HTML tags if any
    s = re.sub(r"\s+", " ", s)       # collapse spaces
    return s.strip().lower()

# ---------- Parse correct_answer into a uniform list ----------
def _as_iterable_correct_values(correct, is_mcq: bool):
    """
    Return a list of acceptable values.

    MCQ:
      - list/tuple -> list
      - JSON list string -> parsed list
      - ANY other string -> [string as-is]  (don't split by commas!)
    Fill-in:
      - list/tuple -> list
      - JSON list string -> parsed list
      - comma-separated string -> split into list
      - otherwise -> [value]
    """
    if isinstance(correct, (list, tuple)):
        return list(correct)

    if isinstance(correct, str):
        cs = correct.strip()
        # JSON-like list?
        if cs.startswith('[') and cs.endswith(']'):
            try:
                loaded = json.loads(cs)
                if isinstance(loaded, list):
                    return loaded
            except Exception:
                pass

        if is_mcq:
            # Single string even if it contains commas (e.g., "Paris, France")
            return [correct]

        # Fill-in: allow comma-separated multi-answers
        if ',' in cs:
            parts = [p.strip() for p in cs.split(',')]
            # if splitting produced >1, treat as multi
            if len(parts) > 1:
                return parts

        return [correct]

    # other scalars
    return [correct]

# ---------- Correctness ----------
def is_correct_answer(q, user_ans):
    if user_ans is None or str(user_ans).strip() == '':
        return False

    correct_raw = q.get('correct_answer')
    is_mcq = bool(q.get('options'))

    acceptable = _as_iterable_correct_values(correct_raw, is_mcq=is_mcq)

    if is_mcq:
        # "No correct answer" override
        if any(isinstance(c, str) and _norm_text(c) == "no correct answer" for c in acceptable):
            return True
        ua = _norm_text(user_ans)
        return any(_norm_text(c) == ua for c in acceptable)

    # Fill-in: numeric any-of
    return any(_equal_numeric(c, user_ans) for c in acceptable)

# ---------- Display ----------
def correct_answer_display(q):
    correct_raw = q.get('correct_answer')
    is_mcq = bool(q.get('options'))
    acceptable = _as_iterable_correct_values(correct_raw, is_mcq=is_mcq)

    if is_mcq and any(isinstance(c, str) and _norm_text(c) == "no correct answer" for c in acceptable):
        return Markup('No correct answer <em>(any choice accepted)</em>')

    rendered = []
    for c in acceptable:
        if isinstance(c, str):
            rendered.append(Markup(c))     # trust your content; use escape(c) if untrusted
        else:
            rendered.append(escape(str(c)))
    return Markup(', ').join(rendered)

# Make available to Jinja
app.jinja_env.globals.update(
    is_correct_answer=is_correct_answer,
    correct_answer_display=correct_answer_display,
    normalize_numeric=_new_normalize_numeric,
    admin_usernames=ADMIN_USERNAMES,
)


@app.route('/api/highlights', methods=['GET'])
def get_highlights():
    if 'user_id' not in session or 'test_session_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    section_idx = request.args.get('section_idx', type=int)
    question_idx = request.args.get('question_idx', type=int)

    if section_idx is None or question_idx is None:
        return jsonify({'error': 'section_idx and question_idx are required'}), 400

    rows = TextHighlight.query.filter_by(
        user_id=session['user_id'],
        test_session_id=session['test_session_id'],
        section_idx=section_idx,
        question_idx=question_idx,
    ).order_by(TextHighlight.start_offset.asc(), TextHighlight.id.asc()).all()

    return jsonify({'highlights': [r.to_dict() for r in rows]})


@app.route('/api/highlights', methods=['POST'])
def create_highlight():
    if 'user_id' not in session or 'test_session_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    data = request.get_json(silent=True) or {}

    section_idx = data.get('section_idx')
    question_idx = data.get('question_idx')
    target = (data.get('target') or '').strip().lower()
    start_offset = data.get('start_offset')
    end_offset = data.get('end_offset')
    selected_text = (data.get('selected_text') or '').strip()

    if target not in {'passage', 'question'}:
        return jsonify({'error': 'Invalid target'}), 400

    if not isinstance(section_idx, int) or not isinstance(question_idx, int):
        return jsonify({'error': 'section_idx and question_idx must be integers'}), 400

    if not isinstance(start_offset, int) or not isinstance(end_offset, int):
        return jsonify({'error': 'start_offset and end_offset must be integers'}), 400

    if start_offset < 0 or end_offset <= start_offset:
        return jsonify({'error': 'Invalid highlight range'}), 400

    if not selected_text:
        return jsonify({'error': 'No selected text'}), 400

    row = TextHighlight(
        user_id=session['user_id'],
        test_session_id=session['test_session_id'],
        section_idx=section_idx,
        question_idx=question_idx,
        target=target,
        start_offset=start_offset,
        end_offset=end_offset,
        selected_text=selected_text,
    )
    db.session.add(row)
    db.session.commit()
    return jsonify({'ok': True, 'highlight': row.to_dict()})


@app.route('/api/highlights/<int:highlight_id>', methods=['DELETE'])
def delete_highlight(highlight_id):
    if 'user_id' not in session or 'test_session_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    row = TextHighlight.query.get_or_404(highlight_id)
    if row.user_id != session['user_id'] or row.test_session_id != session['test_session_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(row)
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/api/highlights/clear', methods=['DELETE'])
def clear_highlights_for_question():
    if 'user_id' not in session or 'test_session_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    data = request.get_json(silent=True) or {}
    section_idx = data.get('section_idx')
    question_idx = data.get('question_idx')

    if not isinstance(section_idx, int) or not isinstance(question_idx, int):
        return jsonify({'error': 'section_idx and question_idx must be integers'}), 400

    TextHighlight.query.filter_by(
        user_id=session['user_id'],
        test_session_id=session['test_session_id'],
        section_idx=section_idx,
        question_idx=question_idx,
    ).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({'ok': True})



def _is_admin():
    return session.get('username') in ADMIN_USERNAMES


@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    if not _is_admin():
        flash('Access denied.')
        return redirect(url_for('dashboard'))

    users = User.query.order_by(User.username).all()

    # Aggregate stats per user
    user_stats = []
    for u in users:
        sessions_all = TestSession.query.filter_by(user_id=u.id).order_by(TestSession.start_time.desc()).all()
        completed = [s for s in sessions_all if s.score is not None]
        in_progress = [s for s in sessions_all if s.score is None]
        latest = sessions_all[0] if sessions_all else None
        user_stats.append({
            'user': u,
            'total': len(sessions_all),
            'completed': len(completed),
            'in_progress': len(in_progress),
            'latest': latest,
        })

    return render_template('admin.html', user_stats=user_stats)


@app.route('/admin/user/<int:user_id>')
def admin_user_detail(user_id):
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    if not _is_admin():
        flash('Access denied.')
        return redirect(url_for('dashboard'))

    u = User.query.get_or_404(user_id)
    test_sessions = TestSession.query.filter_by(user_id=u.id).order_by(TestSession.start_time.desc()).all()

    # Compute scaled scores for each completed session
    session_data = []
    for ts in test_sessions:
        scores = None
        if ts.score is not None:
            answers = json.loads(ts.answers or '{}')
            section_answers = []
            for section_idx in range(len(SECTIONS)):
                qs = get_questions_for_section(section_idx, ts.practice_test_id)
                ans_list = []
                for qid in range(len(qs)):
                    key = f"{section_idx}_{qid}"
                    ans_list.append({'answer': answers.get(key)})
                section_answers.append(ans_list)
            module_multipliers = {
                'verbal': {1: 1.0, 2: 1.66},
                'math':   {1: 0.79, 2: 1.345},
            }
            try:
                scores = compute_section_scores(SECTIONS, ALL_QUESTIONS.get(ts.practice_test_id, []), section_answers, module_multipliers)
            except Exception:
                scores = None
        session_data.append({'session': ts, 'scores': scores})

    return render_template('admin_user_detail.html', u=u, session_data=session_data)


# ===================== DRILL ROUTES =====================

@app.route('/drill_select', methods=['GET'])
def drill_select():
    """Display all drill topics for student selection"""
    if 'user_id' not in session:
        flash('Please log in to start a drill.')
        return redirect(url_for('login'))
    
    topics_by_section = get_drill_topics()
    
    return render_template('drill_select.html', topics_by_section=topics_by_section)


@app.route('/drill_topic/<topic_name>', methods=['GET'])
def drill_topic(topic_name):
    """Display all sets for a specific drill topic"""
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    
    drill_sets = get_drill_sets_for_topic(topic_name)
    if not drill_sets:
        flash(f'No drill sets found for {topic_name}.')
        return redirect(url_for('drill_select'))
    
    # Get user's session history for each set
    user_id = session['user_id']
    sets_with_history = []
    
    for drill_set in drill_sets:
        history = DrillSession.query.filter_by(
            user_id=user_id,
            drill_set_id=drill_set.id
        ).order_by(DrillSession.start_time.desc()).all()
        
        sets_with_history.append({
            'drill_set': drill_set,
            'attempts': len(history),
            'best_score': max([h.accuracy_percent for h in history]) if history else None,
            'latest_score': history[0].accuracy_percent if history else None,
            'latest_date': history[0].start_time if history else None,
        })
    
    drill_sets_data = ALL_QUESTIONS.get('drill_sets', {}).get(topic_name, {})
    description = drill_sets_data.get('description', '')
    
    return render_template('drill_topic.html', 
                         topic_name=topic_name, 
                         description=description,
                         sets_with_history=sets_with_history)


@app.route('/drill_start/<int:drill_set_id>', methods=['POST'])
def drill_start(drill_set_id):
    """Create a new drill session and start drill practice"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    
    use_timer = request.form.get('use_timer', 'false').lower() == 'true'
    
    drill_set = DrillSet.query.get_or_404(drill_set_id)
    
    # Create new drill session
    drill_session = DrillSession(
        user_id=session['user_id'],
        drill_set_id=drill_set_id,
        answers=json.dumps({}),
        use_timer=use_timer
    )
    db.session.add(drill_session)
    db.session.commit()
    
    # Store in session for practice page
    session['drill_session_id'] = drill_session.id
    
    return redirect(url_for('drill_practice', session_id=drill_session.id))


@app.route('/drill/<int:session_id>', methods=['GET', 'POST'])
def drill_practice(session_id):
    """Display drill practice page and handle answer submissions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in.'}), 401
    
    drill_session = DrillSession.query.get_or_404(session_id)
    
    # Verify ownership
    if drill_session.user_id != session['user_id']:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))
    
    # Check if already completed
    if drill_session.end_time is not None:
        return redirect(url_for('drill_results', session_id=session_id))
    
    drill_set = drill_session.drill_set
    question_ids = json.loads(drill_set.question_ids)
    questions = get_skill_questions(question_ids)
    
    if request.method == 'POST':
        data = request.json
        answers = json.loads(drill_session.answers)
        current_question = data.get('current_question', 0)
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        # Save answer
        if answer is not None:
            answers[str(question_id)] = answer
        
        next_question = data.get('next_question')
        
        if next_question is not None and next_question >= len(questions):
            # Drill finished, calculate score
            correct_count = 0
            for q in questions:
                user_answer = answers.get(str(q['question_id']))
                if is_correct_answer(q, user_answer):
                    correct_count += 1
            
            accuracy = (correct_count / len(questions) * 100) if questions else 0
            
            drill_session.answers = json.dumps(answers)
            drill_session.end_time = datetime.utcnow()
            drill_session.duration_seconds = int((datetime.utcnow() - drill_session.start_time).total_seconds())
            drill_session.correct_count = correct_count
            drill_session.total_count = len(questions)
            drill_session.accuracy_percent = accuracy
            
            # Update progress
            progress = DrillSetProgress.query.filter_by(
                user_id=session['user_id'],
                topic_name=drill_set.topic_name
            ).first()
            
            if not progress:
                progress = DrillSetProgress(
                    user_id=session['user_id'],
                    topic_name=drill_set.topic_name,
                    total_attempts=0,
                    completed_sets=0
                )
                db.session.add(progress)
            
            progress.total_attempts += 1
            progress.best_score = max(progress.best_score or 0, accuracy)
            progress.last_attempt_date = datetime.utcnow()
            
            # Count unique drill sets completed at least once for this topic
            completed_set_ids = db.session.query(DrillSession.drill_set_id).join(DrillSet).filter(
                DrillSession.user_id == session['user_id'],
                DrillSet.topic_name == drill_set.topic_name,
                DrillSession.end_time.isnot(None)
            ).distinct().subquery()
            completed_sets_count = db.session.query(completed_set_ids).count()
            
            progress.completed_sets = completed_sets_count
            
            db.session.commit()
            
            return jsonify({'redirect': url_for('drill_results', session_id=session_id)})
        
        drill_session.answers = json.dumps(answers)
        db.session.commit()
        
        # Return next question
        if next_question is not None and next_question < len(questions):
            question = questions[next_question]
            response = {
                'question': question,
                'qid': next_question,
                'session_id': session_id,
                'answer': answers.get(str(question['question_id']), ''),
                'total_questions': len(questions),
                'topic_name': drill_set.topic_name,
                'difficulty': drill_set.difficulty,
                'set_number': drill_set.set_number,
            }
            return jsonify(response)
    
    # GET request - serve practice page
            # Save-only request (next_question is None) — just acknowledge
            return jsonify({'ok': True})
    
        # GET request - serve practice page
    session['drill_session_id'] = session_id
    
    return render_template('drill_practice.html', 
                         session_id=session_id,
                         use_timer=drill_session.use_timer,
                         topic_name=drill_set.topic_name,
                         difficulty=drill_set.difficulty,
                         set_number=drill_set.set_number,
                         total_questions=len(questions))


@app.route('/drill_results/<int:session_id>', methods=['GET'])
def drill_results(session_id):
    """Display results of a completed drill session"""
    if 'user_id' not in session:
        flash('Please log in.')
        return redirect(url_for('login'))
    
    drill_session = DrillSession.query.get_or_404(session_id)
    
    # Verify ownership
    if drill_session.user_id != session['user_id']:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))
    
    # Check if completed
    if drill_session.end_time is None:
        flash('This drill has not been completed yet.')
        return redirect(url_for('drill_practice', session_id=session_id))
    
    drill_set = drill_session.drill_set
    question_ids = json.loads(drill_set.question_ids)
    questions = get_skill_questions(question_ids)
    answers = json.loads(drill_session.answers)
    
    # Build question results with performance breakdown
    question_results = []
    difficulty_breakdown = {}
    
    for q in questions:
        q_id = q['question_id']
        user_answer = answers.get(str(q_id))
        is_correct = is_correct_answer(q, user_answer)
        
        question_results.append({
            'question': q,
            'user_answer': user_answer,
            'is_correct': is_correct,
            'correct_answer': q.get('correct_answer')
        })
        
        # Track by difficulty
        q_level = q.get('level', 'Medium')
        if q_level not in difficulty_breakdown:
            difficulty_breakdown[q_level] = {'correct': 0, 'total': 0}
        difficulty_breakdown[q_level]['total'] += 1
        if is_correct:
            difficulty_breakdown[q_level]['correct'] += 1
    
    # Get user's attempts history on this set
    previous_sessions = DrillSession.query.filter_by(
        user_id=session['user_id'],
        drill_set_id=drill_set.id
    ).order_by(DrillSession.start_time.desc()).limit(10).all()
    
    return render_template('drill_results.html',
                         session=drill_session,
                         drill_set=drill_set,
                         question_results=question_results,
                         difficulty_breakdown=difficulty_breakdown,
                         previous_sessions=previous_sessions)


@app.route('/api/drill/dashboard')
def api_drill_dashboard():
    """Get dashboard data: recent drills + topic progress"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    
    user_id = session['user_id']
    
    # Recent drills (last 5)
    recent_drills = DrillSession.query.filter_by(user_id=user_id).filter(
        DrillSession.end_time.isnot(None)
    ).order_by(DrillSession.end_time.desc()).limit(5).all()
    
    recent_drills_data = []
    for ds in recent_drills:
        recent_drills_data.append({
            'id': ds.id,
            'topic_name': ds.drill_set.topic_name,
            'difficulty': ds.drill_set.difficulty,
            'set_number': ds.drill_set.set_number,
            'accuracy': ds.accuracy_percent,
            'end_time': ds.end_time.isoformat() if ds.end_time else None,
        })
    
    # Topic progress
    progress_data = DrillSetProgress.query.filter_by(user_id=user_id).all()
    
    progress_list = []
    for prog in progress_data:
        progress_list.append({
            'topic_name': prog.topic_name,
            'completed_sets': prog.completed_sets,
            'total_attempts': prog.total_attempts,
            'best_score': prog.best_score,
            'last_attempt_date': prog.last_attempt_date.isoformat() if prog.last_attempt_date else None,
        })
    
    return jsonify({
        'recent_drills': recent_drills_data,
        'topic_progress': progress_list
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_drill_sets()
    app.run(debug=True)