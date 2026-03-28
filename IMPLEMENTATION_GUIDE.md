# Adaptive SAT Testing - Implementation Guide

## Overview

You now have all the components needed to convert your SAT Simulation to an adaptive test. This guide walks you through the integration steps.

## What You Have

### 1. **Adaptive Algorithm Engine** (`adaptive_engine.py`)
   - IRT-based probability calculation
   - Student ability estimation
   - Adaptive question selection
   - Ability tracking and history

### 2. **Database Models** (in `models.py`)
   - `AdaptiveQuestionMetadata` - Stores question difficulty parameters
   - `AdaptiveTestSession` - Tracks student ability over time

### 3. **Integration Module** (`adaptive_integration.py`)
   - Helper functions to initialize metadata
   - Session management
   - Flask route handlers

### 4. **Mockup Questions** (in `database/questions.json`)
   - 31 sample questions across 3 difficulty levels
   - Both Verbal and Math sections
   - Both Module 1 and Module 2

## Integration Steps

### Step 1: Database Setup

First, create the new database tables:

```bash
# In your Flask app context:
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     print("✅ Tables created!")
```

This will create:
- `adaptive_question_metadata` table
- `adaptive_test_sessions` table

### Step 2: Initialize Adaptive Metadata

Before running tests, initialize the metadata for all questions:

```bash
# Option A: Via Flask shell
python3 -c "
from app import app, db, ALL_QUESTIONS
from adaptive_integration import initialize_adaptive_metadata

with app.app_context():
    initialize_adaptive_metadata(db, ALL_QUESTIONS)
"

# Option B: Add to app.py startup
# Add this in your app initialization:
@app.shell_context_processor
def make_shell_context():
    return {'db': db}

@app.before_request
def init_adaptive():
    # Check if metadata initialized
    from models import AdaptiveQuestionMetadata
    if AdaptiveQuestionMetadata.query.count() == 0:
        from adaptive_integration import initialize_adaptive_metadata
        initialize_adaptive_metadata(db, ALL_QUESTIONS)
```

### Step 3: Update app.py

Add these imports at the top:

```python
from adaptive_engine import (
    get_next_adaptive_question,
    update_ability,
    assign_difficulty_metadata,
)
from adaptive_integration import (
    get_or_create_adaptive_session,
    get_next_question_adaptive,
    record_answer,
    register_adaptive_routes,
)
from models import AdaptiveTestSession, AdaptiveQuestionMetadata
```

Register the adaptive routes (after your app initialization):

```python
# After all other routes are defined:
register_adaptive_routes(app, db, ALL_QUESTIONS)
```

### Step 4: Modify Practice Route

Update your `/practice` route to support adaptive selection:

```python
@app.route('/practice', methods=['GET', 'POST'])
def practice():
    # ... existing code ...
    
    # Check if this should be an adaptive test
    is_adaptive = request.args.get('adaptive', 'false').lower() == 'true'
    
    if is_adaptive:
        # Use adaptive question selection
        adaptive_session = get_or_create_adaptive_session(
            test_session.id,
            session['user_id'],
            db
        )
        next_question = get_next_question_adaptive(
            test_session.id,
            test_session,
            ALL_QUESTIONS,
            db
        )
    else:
        # Use existing linear selection
        next_question = get_questions_for_section(
            test_session.current_section,
            test_session.practice_test_id
        )[test_session.current_question]
    
    return render_template('practice.html', question=next_question, ...)
```

### Step 5: Update Answer Submission

Modify the answer submission handler:

```python
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    # ... existing code ...
    
    is_correct = submitted_answer == correct_answer
    
    # Check if adaptive
    adaptive_session = AdaptiveTestSession.query.filter_by(
        test_session_id=test_session_id
    ).first()
    
    if adaptive_session:
        # Record with adaptive tracking
        result = record_answer(
            test_session_id,
            question_id,
            is_correct,
            test_session,
            db
        )
        
        return jsonify({
            'status': 'success',
            'correct': is_correct,
            'ability': result['ability'],
            'level': result['level']
        })
    else:
        # Existing linear test handling
        return jsonify({'status': 'success', 'correct': is_correct})
```

## Frontend Updates (Optional but Recommended)

### Show Ability in Real-Time

Add to your practice.html template:

```html
<div id="ability-indicator" style="display: none;">
    <p>Current Level: <span id="ability-level">Average</span></p>
    <p>Ability: <span id="ability-score">0.0</span></p>
    <progress id="ability-progress" value="50" max="100"></progress>
</div>
```

Add JavaScript to update it:

```javascript
// After each answer is submitted
fetch('/api/adaptive/ability')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('ability-level').textContent = data.level.level;
            document.getElementById('ability-score').textContent = data.ability;
            // Scale to 0-100 for progress bar
            const scaled = ((data.ability + 3) / 6) * 100; // -3 to 3 -> 0 to 100
            document.getElementById('ability-progress').value = scaled;
        }
    });
```

### Show Difficulty Progression

Track which difficulty levels the student has seen:

```html
<div id="difficulty-stats">
    <span>Easy: <span id="easy-count">0</span></span>
    <span>Medium: <span id="medium-count">0</span></span>
    <span>Hard: <span id="hard-count">0</span></span>
</div>
```

Update via API:

```javascript
fetch('/api/adaptive/progress')
    .then(response => response.json())
    .then(data => {
        document.getElementById('easy-count').textContent = data.easy_count;
        document.getElementById('medium-count').textContent = data.medium_count;
        document.getElementById('hard-count').textContent = data.hard_count;
    });
```

## Testing the Implementation

### Test Script

Create a test to verify everything works:

```python
# test_adaptive.py
from app import app, db, ALL_QUESTIONS
from models import User, TestSession, AdaptiveTestSession, AdaptiveQuestionMetadata
from adaptive_integration import initialize_adaptive_metadata
from datetime import datetime

with app.app_context():
    # Clean up test data
    db.session.query(TestSession).delete()
    db.session.query(User).delete()
    db.commit()
    
    # Create test user
    user = User(username='test_user', password='hashed', email='test@example.com')
    db.session.add(user)
    db.commit()
    
    # Create test session
    test_session = TestSession(
        user_id=user.id,
        practice_test_id='Adaptive Test',
        start_time=datetime.utcnow(),
        answers='{}',
        marked_for_review='{}'
    )
    db.session.add(test_session)
    db.commit()
    
    # Create adaptive session
    adaptive_session = AdaptiveTestSession(
        test_session_id=test_session.id,
        user_id=user.id,
        is_adaptive=True,
        current_ability=0.0,
        ability_history='[]',
        answered_question_ids='[]'
    )
    db.session.add(adaptive_session)
    db.commit()
    
    print("✅ Test setup complete!")
    print(f"   User ID: {user.id}")
    print(f"   TestSession ID: {test_session.id}")
    print(f"   AdaptiveTestSession ID: {adaptive_session.id}")
```

Run it:

```bash
python3 test_adaptive.py
```

## Expected Results

### Without Adaptive (Linear Test)
- Student sees all 27 questions per section
- 2+ hours to complete
- Same difficulty sequence for all students

### With Adaptive (Your New System) - Example Performance
| Checkpoint | Ability | Difficulty | Question | Result |
|-----------|---------|------------|----------|--------|
| Start | 0.0 | Medium | Q1 | Correct ✓ |
| Q2 | +0.3 | Hard | Q2 | Wrong ✗ |
| Q3 | +0.1 | Medium | Q3 | Correct ✓ |
| Q4 | +0.4 | Hard | Q4 | Correct ✓ |
| Q5 | +0.7 | Hard+ | Q5 | Wrong ✗ |
| Q10 | +0.4 | Hard | ... | Adapting |

Benefits:
- Personalized difficulty sequence
- More engaging (matched to ability)
- Faster completion (~1.5 hours)
- Better measurement of true ability

## API Reference

### Get Next Question
```
GET/POST /api/adaptive/get-next-question
Response: {
    "status": "success",
    "question": {
        "question_id": 106,
        "type": "verbal",
        "difficulty": -0.2,
        ...
    }
}
```

### Record Answer
```
POST /api/adaptive/record-answer
Body: {
    "question_id": 106,
    "is_correct": true
}
Response: {
    "status": "success",
    "data": {
        "ability": 0.3,
        "history_length": 1,
        "recommendation": "Medium",
        "level": {
            "level": "Average",
            "ability": 0.3,
            "percentile": "50th"
        }
    }
}
```

### Get Current Ability
```
GET /api/adaptive/ability
Response: {
    "status": "success",
    "ability": 0.5,
    "level": {
        "level": "Above Average",
        "ability": 0.5,
        "percentile": "75th"
    },
    "recommendation": "Hard"
}
```

### Get Progress
```
GET /api/adaptive/progress
Response: {
    "status": "success",
    "current_ability": 0.5,
    "questions_answered": 5,
    "ability_history": [...],
    "easy_count": 2,
    "medium_count": 2,
    "hard_count": 1
}
```

## Advanced: Customization

### Adjust Difficulty Progression

In `adaptive_engine.py`, modify these constants:

```python
# More aggressive progression
CORRECT_ANSWER_DELTA = 0.5      # Was 0.3
INCORRECT_ANSWER_DELTA = -0.3   # Was -0.2
```

### Change Initial Ability

```python
INITIAL_ABILITY = 0.5  # Start at medium-hard instead of medium
```

### Customize Difficulty Bands

```python
DIFFICULTY_BOUNDS = {
    'Very Easy': (-1.5, -1.0),
    'Easy': (-1.0, -0.5),
    'Medium': (-0.5, 0.5),
    'Hard': (0.5, 1.0),
    'Very Hard': (1.0, 2.0),
}
```

### Use More Sophisticated Ability Update

In `adaptive_integration.py`, modify `record_answer()`:

```python
from adaptive_engine import advanced_ability_update

new_ability = advanced_ability_update(
    adaptive_session.current_ability,
    is_correct,
    q_difficulty,
    discrimination=metadata.discrimination_index,
    guessing=metadata.guess_parameter
)
```

## Troubleshooting

### "No questions available"
- Check that `ALL_QUESTIONS` is loaded correctly
- Verify questions have proper `type` and `module` fields
- Run `initialize_adaptive_metadata()` to ensure metadata is created

### Ability stuck at 0
- Check that answers are being recorded
- Verify `record_answer()` is being called after each submission
- Look for errors in ability history JSON

### Questions repeating
- Verify `answered_question_ids` is being updated correctly
- Check that session is being persisted to database

## Next Steps

1. ✅ Run database setup and initialization
2. ✅ Test with the "Adaptive Test" test set
3. ✅ Monitor ability progression via `/api/adaptive/progress`
4. ✅ Gather feedback from students
5. ✅ Fine-tune difficulty deltas based on actual usage
6. ✅ Add more custom questions (100+ recommended for production)
7. ✅ Consider IRT calibration with real test data

## Support & Questions

- Review `ADAPTIVE_TEST_PLAN.md` for design details
- Check `adaptive_engine.py` for algorithm implementation
- Look at `adaptive_integration.py` for Flask integration patterns
- Test files: `generate_adaptive_questions.py` shows how to add more questions

Good luck with your adaptive testing system! 🚀
