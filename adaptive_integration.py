"""
Flask Route Integration for Adaptive Testing

This module provides Flask routes and helper functions to integrate
the adaptive testing engine with your Flask application.

Integration with app.py:
1. Import this module in app.py
2. Register routes with your Flask app
3. Use helper functions in your existing routes
"""

import json
import os
from datetime import datetime
from flask import jsonify, request, session

# Import adaptive engine
from adaptive_engine import (
    get_next_adaptive_question,
    update_ability,
    record_ability_checkpoint,
    get_difficulty_recommendation,
    assign_difficulty_metadata,
    estimate_student_level,
    INITIAL_ABILITY
)

# ============================================================================
# INITIALIZATION HELPERS
# ============================================================================

def initialize_adaptive_metadata(db_instance, ALL_QUESTIONS):
    """
    Initialize AdaptiveQuestionMetadata table from questions.json
    
    Call this once at startup or in a migration.
    
    Args:
        db_instance: Flask-SQLAlchemy db instance
        ALL_QUESTIONS: Dictionary of all questions from JSON
    """
    from models import AdaptiveQuestionMetadata
    
    # Count existing metadata
    existing_count = AdaptiveQuestionMetadata.query.count()
    
    if existing_count > 0:
        print(f"✅ AdaptiveQuestionMetadata already initialized ({existing_count} questions)")
        return
    
    metadata_count = 0
    
    # Iterate through all questions and create metadata
    for test_name, questions in ALL_QUESTIONS.items():
        for question in questions:
            q_id = question.get('question_id')
            
            # Check if already exists
            existing = AdaptiveQuestionMetadata.query.filter_by(
                question_id=q_id
            ).first()
            
            if existing:
                continue
            
            # Create new metadata
            metadata = AdaptiveQuestionMetadata(
                question_id=q_id,
                difficulty_parameter=question.get('difficulty', 0.0),
                difficulty_label=question.get('difficulty_label', 'Medium'),
                question_type=question.get('type', 'verbal'),
                module=question.get('module', 1),
                domain=question.get('domain', 'General'),
                skill=question.get('skill', 'General'),
                discrimination_index=1.0,  # Default discrimination
                guess_parameter=0.25,  # 4-choice multiple choice default
            )
            
            db_instance.session.add(metadata)
            metadata_count += 1
        
        # Commit in batches to avoid session overflow
        if metadata_count % 50 == 0:
            db_instance.session.commit()
            print(f"  Added {metadata_count} metadata entries...")
    
    # Final commit
    db_instance.session.commit()
    print(f"✅ Initialized AdaptiveQuestionMetadata with {metadata_count} questions")


# ============================================================================
# SESSION HELPERS
# ============================================================================

def create_adaptive_session(test_session, db_instance):
    """
    Create an AdaptiveTestSession for a given TestSession
    
    Args:
        test_session: TestSession object from database
        db_instance: Flask-SQLAlchemy db instance
        
    Returns:
        AdaptiveTestSession object
    """
    from models import AdaptiveTestSession
    
    # Check if already exists
    existing = AdaptiveTestSession.query.filter_by(
        test_session_id=test_session.id
    ).first()
    
    if existing:
        return existing
    
    # Create new adaptive session
    adaptive_session = AdaptiveTestSession(
        test_session_id=test_session.id,
        user_id=test_session.user_id,
        is_adaptive=True,
        current_ability=INITIAL_ABILITY,
        initial_ability=INITIAL_ABILITY,
        ability_history=json.dumps([]),
        answered_question_ids=json.dumps([])
    )
    
    db_instance.session.add(adaptive_session)
    db_instance.session.commit()
    
    return adaptive_session


def get_or_create_adaptive_session(test_session_id, user_id, db_instance):
    """
    Get existing AdaptiveTestSession or create new one
    
    Args:
        test_session_id: ID of TestSession
        user_id: User ID
        db_instance: Flask-SQLAlchemy db instance
        
    Returns:
        AdaptiveTestSession object
    """
    from models import AdaptiveTestSession, TestSession
    
    # Get adaptive session
    adaptive_session = AdaptiveTestSession.query.filter_by(
        test_session_id=test_session_id
    ).first()
    
    if adaptive_session:
        return adaptive_session
    
    # Create new one
    test_session = TestSession.query.get(test_session_id)
    return create_adaptive_session(test_session, db_instance)


# ============================================================================
# QUESTION SELECTION ROUTES
# ============================================================================

def get_next_question_adaptive(
    test_session_id,
    test_session,
    ALL_QUESTIONS,
    db_instance
):
    """
    Get the next question using adaptive algorithm
    
    Args:
        test_session_id: ID of the test session
        test_session: TestSession object
        ALL_QUESTIONS: Dictionary of all questions
        db_instance: Flask-SQLAlchemy db instance
        
    Returns:
        Question dictionary, or None if test complete
    """
    from models import AdaptiveTestSession
    
    # Get adaptive session
    adaptive_session = get_or_create_adaptive_session(
        test_session_id, 
        test_session.user_id,
        db_instance
    )
    
    # Get list of answered questions
    try:
        answered_ids = set(json.loads(adaptive_session.answered_question_ids))
    except:
        answered_ids = set()
    
    # Get all available questions for this test
    practice_test_id = test_session.practice_test_id
    test_questions = ALL_QUESTIONS.get(practice_test_id, [])
    
    # Assign difficulty metadata if needed
    test_questions = assign_difficulty_metadata(test_questions)
    
    # Get next question based on current ability
    # Filter by current section type and module
    section_type = 'verbal' if test_session.current_section < 2 else 'math'
    section_module = 1 if test_session.current_section % 2 == 0 else 2
    
    next_question = get_next_adaptive_question(
        all_questions=test_questions,
        current_ability=adaptive_session.current_ability,
        answered_question_ids=answered_ids,
        question_type=section_type,
        module=section_module
    )
    
    return next_question


def record_answer(
    test_session_id,
    question_id,
    is_correct,
    test_session,
    db_instance
):
    """
    Record an answer and update ability estimate
    
    Args:
        test_session_id: ID of test session
        question_id: ID of question answered
        is_correct: Whether answer was correct
        test_session: TestSession object
        db_instance: Flask-SQLAlchemy db instance
        
    Returns:
        Updated adaptive session data
    """
    from models import AdaptiveTestSession, AdaptiveQuestionMetadata
    
    # Get adaptive session
    adaptive_session = get_or_create_adaptive_session(
        test_session_id,
        test_session.user_id,
        db_instance
    )
    
    # Get question metadata
    metadata = AdaptiveQuestionMetadata.query.filter_by(
        question_id=question_id
    ).first()
    
    q_difficulty = metadata.difficulty_parameter if metadata else 0.0
    
    # Update ability
    new_ability = update_ability(
        adaptive_session.current_ability,
        is_correct,
        q_difficulty
    )
    
    # Record checkpoint
    new_history = record_ability_checkpoint(
        adaptive_session.ability_history,
        question_id,
        new_ability,
        is_correct
    )
    
    # Update answered questions
    try:
        answered_ids = set(json.loads(adaptive_session.answered_question_ids))
    except:
        answered_ids = set()
    
    answered_ids.add(question_id)
    
    # Update difficulty distribution
    if is_correct:
        if q_difficulty < -0.5:
            adaptive_session.easy_count += 1
        elif q_difficulty > 0.5:
            adaptive_session.hard_count += 1
        else:
            adaptive_session.medium_count += 1
    
    # Save updates
    adaptive_session.current_ability = new_ability
    adaptive_session.ability_history = new_history
    adaptive_session.answered_question_ids = json.dumps(list(answered_ids))
    adaptive_session.previous_difficulty = q_difficulty
    adaptive_session.updated_at = datetime.utcnow()
    
    # Update metadata statistics
    if metadata:
        metadata.total_attempts += 1
        if is_correct:
            metadata.correct_attempts += 1
        metadata.updated_at = datetime.utcnow()
    
    db_instance.session.commit()
    
    return {
        'ability': round(new_ability, 3),
        'history_length': len(json.loads(new_history)),
        'recommendation': get_difficulty_recommendation(new_ability),
        'level': estimate_student_level(new_ability)
    }


# ============================================================================
# API ENDPOINTS (to be registered with Flask app)
# ============================================================================

def register_adaptive_routes(app, db_instance, ALL_QUESTIONS):
    """
    Register adaptive testing routes with Flask app
    
    Call this in your app.py:
        register_adaptive_routes(app, db, ALL_QUESTIONS)
    
    Args:
        app: Flask application instance
        db_instance: Flask-SQLAlchemy db instance
        ALL_QUESTIONS: Dictionary of all questions
    """
    
    @app.route('/api/adaptive/init', methods=['POST'])
    def init_adaptive():
        """Initialize adaptive testing metadata"""
        try:
            initialize_adaptive_metadata(db_instance, ALL_QUESTIONS)
            return jsonify({'status': 'success', 'message': 'Adaptive testing initialized'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/adaptive/get-next-question', methods=['GET', 'POST'])
    def get_next():
        """Get next adaptive question"""
        if 'user_id' not in session or 'test_session_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            from models import TestSession
            
            test_session_id = session['test_session_id']
            test_session = TestSession.query.get(test_session_id)
            
            if not test_session:
                return jsonify({'error': 'Test session not found'}), 404
            
            next_question = get_next_question_adaptive(
                test_session_id,
                test_session,
                ALL_QUESTIONS,
                db_instance
            )
            
            if not next_question:
                return jsonify({
                    'status': 'test_complete',
                    'message': 'No more questions available'
                })
            
            return jsonify({
                'status': 'success',
                'question': next_question
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/adaptive/record-answer', methods=['POST'])
    def record():
        """Record an answer and get ability update"""
        if 'user_id' not in session or 'test_session_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            from models import TestSession
            
            data = request.json
            question_id = data.get('question_id')
            is_correct = data.get('is_correct', False)
            
            test_session_id = session['test_session_id']
            test_session = TestSession.query.get(test_session_id)
            
            if not test_session:
                return jsonify({'error': 'Test session not found'}), 404
            
            result = record_answer(
                test_session_id,
                question_id,
                is_correct,
                test_session,
                db_instance
            )
            
            return jsonify({
                'status': 'success',
                'data': result
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/adaptive/ability', methods=['GET'])
    def get_ability():
        """Get current ability estimate"""
        if 'user_id' not in session or 'test_session_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            from models import AdaptiveTestSession
            
            test_session_id = session['test_session_id']
            adaptive_session = AdaptiveTestSession.query.filter_by(
                test_session_id=test_session_id
            ).first()
            
            if not adaptive_session:
                return jsonify({'error': 'Adaptive session not found'}), 404
            
            return jsonify({
                'status': 'success',
                'ability': round(adaptive_session.current_ability, 3),
                'level': estimate_student_level(adaptive_session.current_ability),
                'recommendation': get_difficulty_recommendation(adaptive_session.current_ability)
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/adaptive/progress', methods=['GET'])
    def get_progress():
        """Get test progress and ability history"""
        if 'user_id' not in session or 'test_session_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            from models import AdaptiveTestSession
            
            test_session_id = session['test_session_id']
            adaptive_session = AdaptiveTestSession.query.filter_by(
                test_session_id=test_session_id
            ).first()
            
            if not adaptive_session:
                return jsonify({'error': 'Adaptive session not found'}), 404
            
            try:
                history = json.loads(adaptive_session.ability_history)
            except:
                history = []
            
            return jsonify({
                'status': 'success',
                'current_ability': round(adaptive_session.current_ability, 3),
                'questions_answered': len(history),
                'ability_history': history[-20:],  # Last 20 checkpoints
                'easy_count': adaptive_session.easy_count,
                'medium_count': adaptive_session.medium_count,
                'hard_count': adaptive_session.hard_count
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# ============================================================================
# EXAMPLE: How to use in app.py
# ============================================================================

"""
# In your app.py, add:

from adaptive_integration import (
    initialize_adaptive_metadata,
    register_adaptive_routes
)

# After creating your Flask app and db:
app = Flask(__name__)
db = SQLAlchemy(app)

# ... your other routes ...

# Initialize and register adaptive testing
with app.app_context():
    db.create_all()  # Create tables
    initialize_adaptive_metadata(db, ALL_QUESTIONS)

register_adaptive_routes(app, db, ALL_QUESTIONS)

# Now you can use:
# - GET/POST /api/adaptive/init
# - GET/POST /api/adaptive/get-next-question
# - POST /api/adaptive/record-answer
# - GET /api/adaptive/ability
# - GET /api/adaptive/progress
"""
