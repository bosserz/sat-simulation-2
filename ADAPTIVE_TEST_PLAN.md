# Adaptive SAT Testing System - Implementation Guide

## Overview
This document outlines how to convert your SAT Simulation from a linear test to an **adaptive test** where question difficulty adjusts based on student performance.

## What is Adaptive Testing?

Adaptive testing dynamically adjusts the difficulty of questions based on a student's previous answers:
- **Correct answer** → Next question is harder
- **Incorrect answer** → Next question is easier

This approach:
- ✅ Makes tests more efficient (fewer questions needed)
- ✅ Reduces test fatigue (balanced difficulty)
- ✅ Provides better ability estimation
- ✅ More engaging and personalized

## Implementation Approach: Simplified IRT-Based Algorithm

We'll use a simplified Item Response Theory (IRT) approach:

### Key Concepts

1. **Question Difficulty (θ)**
   - Easy: -1.0 to -0.5
   - Medium: -0.5 to 0.5
   - Hard: 0.5 to 1.5

2. **Student Ability (θ_student)**
   - Starts at 0 (medium difficulty)
   - Updates after each answer
   - Represents estimated ability

3. **Difficulty Adjustment**
   - After correct answer: Increase difficulty (+0.3)
   - After incorrect answer: Decrease difficulty (-0.2)

### Algorithm Flow

```
1. Start: θ_student = 0.0 (medium difficulty)
2. Select question closest to student's current θ
3. Student answers
4. IF correct:
   - θ_student += 0.3
   - Fetch harder question
5. ELSE:
   - θ_student -= 0.2
   - Fetch easier question
6. Continue until test complete
```

## Database Schema Changes

### New Table: `adaptive_question_metadata`
Track question-specific adaptive parameters:
- `question_id` - FK to Question
- `difficulty_parameter` (θ) - Real number (-1.5 to 2.0)
- `discrimination_index` - Question's ability to distinguish
- `guess_parameter` - Probability of correct guess
- `total_attempts` - For statistics
- `correct_attempts` - For statistics

### Updated `TestSession` Model
Add fields for adaptive testing:
- `current_ability` - Student's estimated ability (θ)
- `ability_history` - JSON: track ability over time
- `previous_difficulty` - Last question's difficulty
- `adaptive_mode` - Boolean: is this adaptive?

## Mockup Questions Structure

Each question will include:
```json
{
  "question_id": 1,
  "type": "verbal",
  "module": 1,
  "domain": "Craft and Structure",
  "difficulty": -1.0,  // Easy (-1.0 to -0.5)
  "difficulty_label": "Easy",
  "skill": "Words in Context",
  "passage": "...",
  "question": "Which choice completes...",
  "options": [...],
  "correct_answer": "...",
  "explanation": "..."
}
```

## Questions by Difficulty Level

### Easy Questions (θ: -1.0 to -0.5)
- Straightforward vocabulary
- Clear context clues
- Simple grammar
- ~70-80% of test-takers answer correctly

### Medium Questions (θ: -0.5 to 0.5)
- Moderate vocabulary
- Require inference
- Some grammatical complexity
- ~50% of test-takers answer correctly

### Hard Questions (θ: 0.5 to 1.5)
- Advanced vocabulary
- Subtle context clues
- Complex sentence structure
- ~20-30% of test-takers answer correctly

## Implementation Steps

1. ✅ Create adaptive question metadata model
2. ✅ Generate 60+ mockup questions across difficulty levels
3. ✅ Implement adaptive selection algorithm
4. ✅ Update TestSession to track ability
5. ✅ Create `get_next_adaptive_question()` function
6. ✅ Modify `/practice` route to use adaptive selection
7. ✅ Update score calculation for adaptive tests
8. ✅ Add ability visualization to results page

## Expected Benefits

| Metric | Linear Test | Adaptive Test |
|--------|------------|---------------|
| Questions per section | 27 | 15-20 |
| Test Duration | 2+ hours | 1.5 hours |
| Engagement | Moderate | High |
| Measurement Precision | Good | Excellent |

## Testing Strategy

1. Generate mockup questions (3 difficulty levels per skill)
2. Test with sample user data
3. Verify ability tracking works correctly
4. Validate question selection logic
5. Compare results with linear test

---

Next steps: Generate mockup questions and implement the database models.
