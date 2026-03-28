# Adaptive Testing - Quick Start Guide

## 📋 Summary

Your SAT Simulation now has full adaptive testing support! This means:

✅ Questions adjust difficulty based on student performance
✅ Better measurement of student ability
✅ More engaging student experience
✅ Reduced test fatigue
✅ Faster test completion

## 🚀 Quick Setup (5 minutes)

### 1. Create Database Tables
```bash
python3 << 'EOF'
from app import app, db

with app.app_context():
    db.create_all()
    print("✅ Database tables created!")
EOF
```

### 2. Initialize Question Metadata
```bash
python3 << 'EOF'
from app import app, db, ALL_QUESTIONS
from adaptive_integration import initialize_adaptive_metadata

with app.app_context():
    initialize_adaptive_metadata(db, ALL_QUESTIONS)
    print("✅ Question metadata initialized!")
EOF
```

### 3. Update app.py (copy the imports and registration below)

Find these lines in your `app.py`:
```python
from flask import Flask, render_template, ...
from flask_sqlalchemy import SQLAlchemy
```

Add after the imports:
```python
# Adaptive Testing Imports
from adaptive_engine import assign_difficulty_metadata
from adaptive_integration import register_adaptive_routes
from models import AdaptiveTestSession, AdaptiveQuestionMetadata
```

Then, **at the very end of app.py**, add:
```python
# Register adaptive testing routes
register_adaptive_routes(app, db, ALL_QUESTIONS)

# Initialize metadata on startup
@app.shell_context_processor
def make_shell_context():
    return {'db': db}
```

### 4. Done! 🎉

That's it! Your app now supports adaptive testing.

## 📖 How It Works

### The Algorithm

1. **Student starts with ability = 0** (medium difficulty)
2. **System selects a question** close to their current ability
3. **Student answers**
4. **Ability updates automatically:**
   - Correct answer: ability += 0.3 (asks harder questions)
   - Wrong answer: ability -= 0.2 (asks easier questions)
5. **Repeat until test complete**

### Example Session

| Question # | Ability | Difficulty | Question | Answer | New Ability |
|-----------|---------|-----------|----------|--------|------------|
| 1 | 0.0 | Medium | Easy vocab | ✓ | **0.3** |
| 2 | 0.3 | Medium | Medium vocab | ✓ | **0.6** |
| 3 | 0.6 | Hard | Complex grammar | ✗ | **0.4** |
| 4 | 0.4 | Medium | Hard context clues | ✓ | **0.7** |
| 5 | 0.7 | Hard | Advanced passage | ✓ | **1.0** |

## 🧪 Test the Implementation

### Create a Test User and Session
```bash
python3 << 'EOF'
from app import app, db
from models import User, TestSession, AdaptiveTestSession
from datetime import datetime

with app.app_context():
    # Create user
    user = User(username='demo_user', password='hashed_pwd', email='demo@test.com')
    db.session.add(user)
    db.session.commit()
    
    # Create linear test session
    test_session = TestSession(
        user_id=user.id,
        practice_test_id='Adaptive Test',
        start_time=datetime.utcnow(),
        answers='{}',
        marked_for_review='{}'
    )
    db.session.add(test_session)
    db.session.commit()
    
    # Create adaptive tracking
    adaptive_session = AdaptiveTestSession(
        test_session_id=test_session.id,
        user_id=user.id,
        is_adaptive=True,
        current_ability=0.0,
        ability_history='[]',
        answered_question_ids='[]'
    )
    db.session.add(adaptive_session)
    db.session.commit()
    
    print("✅ Test setup complete!")
    print(f"   User: {user.username}")
    print(f"   Test Session: {test_session.id}")
EOF
```

### Simulate Questions and Answers
```bash
python3 << 'EOF'
from app import app, db, ALL_QUESTIONS
from models import TestSession, AdaptiveTestSession
from adaptive_integration import get_next_question_adaptive, record_answer

with app.app_context():
    # Get the test session we just created
    test_session = TestSession.query.filter_by(practice_test_id='Adaptive Test').first()
    adaptive_session = AdaptiveTestSession.query.filter_by(
        test_session_id=test_session.id
    ).first()
    
    print("=== ADAPTIVE TEST SIMULATION ===\n")
    print(f"Initial Ability: {adaptive_session.current_ability}")
    
    # Simulate 5 answers
    for i in range(5):
        # Get next question
        next_q = get_next_question_adaptive(
            test_session.id,
            test_session,
            ALL_QUESTIONS,
            db
        )
        
        if not next_q:
            print("✗ No more questions!")
            break
        
        # Simulate answer (alternating correct/wrong for demo)
        is_correct = (i % 2 == 0)
        
        # Record answer
        result = record_answer(
            test_session.id,
            next_q['question_id'],
            is_correct,
            test_session,
            db
        )
        
        # Refresh adaptive session
        db.session.refresh(adaptive_session)
        
        status = "✓" if is_correct else "✗"
        print(f"\nQ{i+1}: {status} {next_q['question_id']}")
        print(f"   Difficulty: {next_q.get('difficulty_label')}")
        print(f"   New Ability: {result['ability']}")
        print(f"   Level: {result['level']['level']}")
        print(f"   Recommendation: {result['recommendation']}")

EOF
```

## 📊 Files Created/Modified

### NEW Files:
- `adaptive_engine.py` - Core IRT algorithm
- `adaptive_integration.py` - Flask integration helpers
- `ADAPTIVE_TEST_PLAN.md` - Design documentation
- `IMPLEMENTATION_GUIDE.md` - Full integration guide
- `QUICK_START.md` - This file
- `generate_adaptive_questions.py` - Question generation script

### Modified Files:
- `models.py` - Added AdaptiveQuestionMetadata and AdaptiveTestSession classes
- `database/questions.json` - Added 31 mockup questions

## 🎯 Next Steps

### For Testing
1. Create a test user: `User(username='test', email='test@ex.com')`
2. Start a test session: `TestSession(..., practice_test_id='Adaptive Test')`
3. Call `/api/adaptive/get-next-question` to get questions
4. Call `/api/adaptive/record-answer` after each answer
5. Call `/api/adaptive/ability` to check ability estimate

### For Production
1. ✅ Add more questions (aim for 100+)
2. ✅ Test with real students
3. ✅ Calibrate difficulty parameters based on actual data
4. ✅ Consider IRT calibration using real test data
5. ✅ Add results visualization page showing ability curve
6. ✅ Create teacher dashboard to view student ability trends

### For Customization
See IMPLEMENTATION_GUIDE.md for:
- Adjusting difficulty progression
- Changing initial ability
- Using advanced ability updates
- Custom difficulty bands

## 🔧 Useful API Endpoints

```bash
# Get next question
curl -X GET http://localhost:5000/api/adaptive/get-next-question

# Record an answer
curl -X POST http://localhost:5000/api/adaptive/record-answer \
  -H "Content-Type: application/json" \
  -d '{"question_id": 106, "is_correct": true}'

# Get current ability
curl -X GET http://localhost:5000/api/adaptive/ability

# Get full progress
curl -X GET http://localhost:5000/api/adaptive/progress
```

## ❓ FAQ

**Q: Can I use adaptive and linear tests simultaneously?**
A: Yes! Set `is_adaptive=true` on TestSession to enable adaptive mode.

**Q: How do I add more questions?**
A: Edit `generate_adaptive_questions.py` and run it again, or use the pattern shown there.

**Q: What if a student gets all questions right?**
A: Ability caps at 3.0 (MAX_ABILITY). Their questions will be extremely hard.

**Q: Can I see ability progression?**
A: Yes! `/api/adaptive/progress` returns ability_history JSON with all checkpoints.

**Q: Is the algorithm actually IRT?**
A: It's a **simplified** IRT using the 3-Parameter Logistic model. See `adaptive_engine.py` for details.

## 📚 Learn More

- **Algorithm Details**: See `adaptive_engine.py` docstrings
- **Integration Details**: See `IMPLEMENTATION_GUIDE.md`
- **Design Rationale**: See `ADAPTIVE_TEST_PLAN.md`
- **Question Format**: Check `database/questions.json` for examples

## 💡 Pro Tips

1. **Monitor ability divergence**: Check if different students' abilities diverge appropriately
2. **Track test reliability**: Use `calculate_test_info()` in adaptive_engine.py
3. **A/B test**: Run parallel adaptive vs linear tests to compare effectiveness
4. **Calibrate questions**: Update difficulty_parameter values based on real performance data
5. **Visualize progression**: Add an ability curve chart to student results page

## ✅ Validation Checklist

- [ ] Database tables created
- [ ] Metadata initialized
- [ ] Imports added to app.py
- [ ] Routes registered
- [ ] Test user created
- [ ] Test question answered
- [ ] Ability updated correctly
- [ ] Next question difficulty adjusted
- [ ] API endpoints working

## 🆘 Issues?

1. **Database errors**: Run `python3 -c "from app import app, db; app.app_context().push(); db.create_all()"`
2. **Import errors**: Make sure all new files are in same directory as app.py
3. **No questions**: Check `ALL_QUESTIONS` is loaded and contains "Adaptive Test"
4. **Ability not updating**: Debug with `print()` statements in `record_answer()`

---

**You're all set! 🎓 Start using adaptive testing in your SAT simulation app!**
