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

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Set SQLAlchemy configuration
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///sat_practice.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if DATABASE_URL:
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
                    test_session.section_start_time = datetime.utcnow()
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
            'answer': answers.get(f"{test_session.current_section}_{current_question}", ''),
            'marked': marked.get(f"{test_session.current_section}_{current_question}", False),
            'total_questions': len(section_questions),
            'section_name': SECTIONS[test_session.current_section]['name']
        }
        print(f"Returning question data: {response}")  # Debugging
        return jsonify(response)
    
    section_duration = SECTIONS[test_session.current_section]['duration']

    if test_session.section_start_time:
        elapsed = (datetime.utcnow() - test_session.section_start_time).total_seconds()
    else:
        # In case section_start_time was never set
        test_session.section_start_time = datetime.utcnow()
        db.session.commit()
        elapsed = 0

    remaining_time = max(0, section_duration - int(elapsed))

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

# @app.route('/results/<int:session_id>')
# def results(session_id):
#     if 'user_id' not in session:
#         flash('Please log in to view results.')
#         return redirect(url_for('login'))
    
#     test_session = TestSession.query.get_or_404(session_id)
#     if test_session.user_id != session['user_id']:
#         flash('Unauthorized access.')
#         return redirect(url_for('dashboard'))
    
#     practice_test_id = test_session.practice_test_id
#     answers = json.loads(test_session.answers)
#     marked = json.loads(test_session.marked_for_review)
    
#     # Calculate section scores
#     section_scores = {}
#     section_answers = {}
#     for section_idx in range(len(SECTIONS)):
#         section_questions = get_questions_for_section(section_idx, practice_test_id)
#         section_score = 0
#         section_ans = {}
#         for qid in range(len(section_questions)):
#             answer_key = f"{section_idx}_{qid}"
#             ans = answers.get(answer_key)
#             if ans and section_questions[qid]['correct_answer'] == ans:
#                 section_score += 1
#             section_ans[qid] = {
#                 'answer': ans,
#                 'marked': marked.get(answer_key, False)
#             }
#         section_scores[section_idx] = section_score
#         section_answers[section_idx] = section_ans

#     # result = supabase.table("questions").select("*").eq("test", practice_test_id).order("id").execute()
#     # questions = result.data
    
#     return render_template(
#         'results.html',
#         score=test_session.score,
#         section_scores=section_scores,
#         section_answers=section_answers,
#         sections=SECTIONS,
#         questions=ALL_QUESTIONS[practice_test_id]
#     )

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)