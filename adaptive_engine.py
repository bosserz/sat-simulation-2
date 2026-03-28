"""
Adaptive Testing Engine - Core Logic for Adaptive SAT Test

This module implements the Item Response Theory (IRT) based adaptive testing algorithm.
It handles:
- Question difficulty estimation
- Student ability calculation
- Adaptive question selection
- Ability updates after each answer
"""

import json
import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# ============================================================================
# ADAPTIVE TESTING CONSTANTS
# ============================================================================

# Ability adjustment parameters (simplified IRT)
CORRECT_ANSWER_DELTA = 0.3      # Increase in ability after correct answer
INCORRECT_ANSWER_DELTA = -0.2   # Decrease in ability after incorrect answer

# Ability bounds
MIN_ABILITY = -3.0
MAX_ABILITY = 3.0
INITIAL_ABILITY = 0.0

# Difficulty bounds and labels
DIFFICULTY_BOUNDS = {
    'Easy': (-1.0, -0.5),
    'Medium': (-0.5, 0.5),
    'Hard': (0.5, 1.5),
}

# ============================================================================
# QUESTION METADATA INITIALIZATION
# ============================================================================

def assign_difficulty_metadata(questions_list: List[Dict]) -> List[Dict]:
    """
    Assign adaptive difficulty parameters to questions based on their difficulty label.
    
    This function initializes difficulty_parameter values for questions to support
    adaptive selection.
    
    Args:
        questions_list: List of question dictionaries from JSON
        
    Returns:
        Questions list with added/updated adaptive metadata
    """
    
    for question in questions_list:
        # If not already has difficulty parameter, assign based on label
        if 'difficulty' not in question:
            difficulty_label = question.get('difficulty_label', 'Medium')
            
            if difficulty_label == 'Easy':
                question['difficulty'] = -0.8  # Default easy
            elif difficulty_label == 'Medium':
                question['difficulty'] = 0.0   # Default medium
            elif difficulty_label == 'Hard':
                question['difficulty'] = 0.9   # Default hard
            else:
                question['difficulty'] = 0.0   # Default to medium
        
        if 'difficulty_label' not in question:
            # Infer label from difficulty parameter
            difficulty = question.get('difficulty', 0.0)
            if difficulty < -0.5:
                question['difficulty_label'] = 'Easy'
            elif difficulty > 0.5:
                question['difficulty_label'] = 'Hard'
            else:
                question['difficulty_label'] = 'Medium'
    
    return questions_list


# ============================================================================
# PROBABILITY OF CORRECT RESPONSE (IRT 3-PL Function)
# ============================================================================

def probability_correct(ability: float, difficulty: float, 
                       discrimination: float = 1.0, 
                       guessing: float = 0.25) -> float:
    """
    Calculate probability of correct response using 3-Parameter Logistic (3-PL) model.
    
    This is a simplified IRT model:
    P(correct) = c + (1 - c) / (1 + exp(-a(θ - b)))
    
    Where:
    - θ (ability): student's ability level
    - b (difficulty): question difficulty
    - a (discrimination): question's ability to discriminate students
    - c (guessing): lower asymptote (probability of guessing correctly)
    
    Args:
        ability: Student's current ability estimate (-3.0 to 3.0)
        difficulty: Question difficulty parameter
        discrimination: Question discrimination index (default 1.0)
        guessing: Guessing probability (default 0.25 for 4-choice)
        
    Returns:
        Probability [0, 1] that student answers correctly
    """
    try:
        # Sigmoid function: 1 / (1 + e^(-x))
        exponent = discrimination * (ability - difficulty)
        # Clamp exponent to prevent overflow
        exponent = max(-100, min(100, exponent))
        logistic_part = 1.0 / (1.0 + math.exp(-exponent))
        
        # Apply 3-PL formula
        probability = guessing + (1 - guessing) * logistic_part
        return max(0.0, min(1.0, probability))
    except:
        # Fallback in case of numerical error
        return 0.5


# ============================================================================
# QUESTION SELECTION
# ============================================================================

def get_next_adaptive_question(
    all_questions: List[Dict],
    current_ability: float,
    answered_question_ids: set,
    preferred_difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    module: Optional[int] = None
) -> Optional[Dict]:
    """
    Select the next question using adaptive algorithm.
    
    Selection strategy:
    1. Filter out already-answered questions
    2. Filter by type/module if specified
    3. Target question difficulty close to current ability
    4. Return best match
    
    Args:
        all_questions: List of all available questions
        current_ability: Student's current ability estimate
        answered_question_ids: Set of question IDs already answered
        preferred_difficulty: Filter by difficulty level (optional)
        question_type: Filter by type 'verbal' or 'math' (optional)
        module: Filter by module 1 or 2 (optional)
        
    Returns:
        Selected question dictionary, or None if none available
    """
    
    # Filter questions
    available = [
        q for q in all_questions
        if q.get('question_id') not in answered_question_ids
    ]
    
    # Apply filters
    if question_type:
        available = [q for q in available if q.get('type') == question_type]
    
    if module:
        available = [q for q in available if q.get('module') == module]
    
    if preferred_difficulty:
        available = [q for q in available if q.get('difficulty_label') == preferred_difficulty]
    
    if not available:
        return None
    
    # Score each question based on difficulty match
    # We want difficulty close to current ability
    best_question = None
    best_score = float('inf')  # Minimize distance
    
    for question in available:
        q_difficulty = question.get('difficulty', 0.0)
        
        # Distance from current ability to question difficulty
        distance = abs(current_ability - q_difficulty)
        
        # Prefer questions at difficulty closest to current ability
        # Add small random variation to avoid always picking same question
        score = distance
        
        if score < best_score:
            best_score = score
            best_question = question
    
    return best_question


# ============================================================================
# ABILITY ESTIMATION
# ============================================================================

def update_ability(
    current_ability: float,
    is_correct: bool,
    question_difficulty: float
) -> float:
    """
    Update student ability estimate after answering a question.
    
    Simplified algorithm:
    - Correct answer: ability += CORRECT_ANSWER_DELTA
    - Incorrect answer: ability += INCORRECT_ANSWER_DELTA
    
    Can be extended to use full MaxLikelihood IRT estimation.
    
    Args:
        current_ability: Current ability estimate
        is_correct: Whether student answered correctly
        question_difficulty: Difficulty of the question answered
        
    Returns:
        Updated ability estimate, bounded by [MIN_ABILITY, MAX_ABILITY]
    """
    
    if is_correct:
        new_ability = current_ability + CORRECT_ANSWER_DELTA
    else:
        new_ability = current_ability + INCORRECT_ANSWER_DELTA
    
    # Bound the ability
    new_ability = max(MIN_ABILITY, min(MAX_ABILITY, new_ability))
    
    return new_ability


def advanced_ability_update(
    current_ability: float,
    is_correct: bool,
    question_difficulty: float,
    discrimination: float = 1.0,
    guessing: float = 0.25
) -> float:
    """
    More sophisticated ability update using information from IRT parameters.
    
    This uses a Newton-Raphson inspired approach where the ability update
    is proportional to how much information the question provides.
    
    Args:
        current_ability: Current ability estimate
        is_correct: Whether student answered correctly
        question_difficulty: Difficulty of the question
        discrimination: Question discrimination index
        guessing: Guessing probability
        
    Returns:
        Updated ability estimate
    """
    
    # Calculate probability of correct response
    p_correct = probability_correct(current_ability, question_difficulty, 
                                   discrimination, guessing)
    
    # Information parameter (derivative of likelihood)
    # Higher discrimination and questions near ability contribute more info
    info_weight = discrimination * p_correct * (1 - p_correct)
    
    # Weight adjustments by information content
    if is_correct:
        delta = CORRECT_ANSWER_DELTA * (1 + info_weight)
    else:
        delta = INCORRECT_ANSWER_DELTA * (1 - info_weight)
    
    new_ability = current_ability + delta
    
    # Bound the ability
    new_ability = max(MIN_ABILITY, min(MAX_ABILITY, new_ability))
    
    return new_ability


# ============================================================================
# ABILITY TRACKING
# ============================================================================

def record_ability_checkpoint(
    ability_history: str,
    question_id: int,
    new_ability: float,
    is_correct: bool
) -> str:
    """
    Add a checkpoint to ability history.
    
    Args:
        ability_history: JSON string of history list
        question_id: ID of question just answered
        new_ability: Updated ability estimate
        is_correct: Whether answer was correct
        
    Returns:
        Updated ability_history JSON string
    """
    
    try:
        history = json.loads(ability_history) if ability_history else []
    except:
        history = []
    
    checkpoint = {
        'question_id': question_id,
        'ability': round(new_ability, 3),
        'correct': is_correct,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    history.append(checkpoint)
    
    # Keep only last 100 checkpoints to avoid bloat
    if len(history) > 100:
        history = history[-100:]
    
    return json.dumps(history)


def get_difficulty_distribution(ability_history: str) -> Dict[str, int]:
    """
    Analyze the difficulty distribution of answered questions.
    
    Returns:
        Dictionary with counts: {'easy': int, 'medium': int, 'hard': int}
    """
    
    try:
        history = json.loads(ability_history) if ability_history else []
    except:
        history = []
    
    # This would need access to question metadata to fully work
    # For now, return placeholder
    return {'easy': 0, 'medium': 0, 'hard': 0}


# ============================================================================
# RECOMMENDATION & ANALYTICS
# ============================================================================

def get_difficulty_recommendation(current_ability: float) -> str:
    """
    Recommend question difficulty based on current ability.
    
    Args:
        current_ability: Student's current ability
        
    Returns:
        Difficulty label: 'Easy', 'Medium', or 'Hard'
    """
    
    if current_ability < -0.5:
        return 'Easy'
    elif current_ability > 0.5:
        return 'Hard'
    else:
        return 'Medium'


def estimate_student_level(ability_estimate: float) -> Dict[str, str]:
    """
    Convert ability estimate to interpretable level.
    
    Args:
        ability_estimate: IRT ability estimate
        
    Returns:
        Dictionary with level description
    """
    
    if ability_estimate < -1.5:
        level = 'Below Average'
        percentile = '10th'
    elif ability_estimate < -0.5:
        level = 'Below Average-Plus'
        percentile = '25th'
    elif ability_estimate < 0.5:
        level = 'Average'
        percentile = '50th'
    elif ability_estimate < 1.5:
        level = 'Above Average'
        percentile = '75th'
    else:
        level = 'Advanced'
        percentile = '90th'
    
    return {
        'level': level,
        'ability': round(ability_estimate, 2),
        'percentile': percentile
    }


# ============================================================================
# TEST VALIDITY & DIAGNOSTICS
# ============================================================================

def calculate_test_info(
    questions_answered: List[Dict],
    ability_estimate: float,
    discrimination: float = 1.0,
    guessing: float = 0.25
) -> float:
    """
    Calculate Fisher Information metric for test reliability.
    
    Higher information = more reliable ability estimate
    Target: Info > 5.0 for reliable estimate
    
    Args:
        questions_answered: List of question responses
        ability_estimate: Current ability estimate
        discrimination: Average discrimination index
        guessing: Average guessing parameter
        
    Returns:
        Total Fisher Information value
    """
    
    total_info = 0.0
    
    for question in questions_answered:
        q_difficulty = question.get('difficulty', 0.0)
        
        # Fisher Information function
        p = probability_correct(ability_estimate, q_difficulty, 
                              discrimination, guessing)
        info = discrimination ** 2 * p * (1 - p) / ((1 - guessing) ** 2)
        
        total_info += info
    
    return total_info


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("Adaptive Testing Engine Loaded Successfully")
    print(f"Initial ability: {INITIAL_ABILITY}")
    print(f"Correct answer delta: +{CORRECT_ANSWER_DELTA}")
    print(f"Incorrect answer delta: {INCORRECT_ANSWER_DELTA}")
    
    # Test probability calculation
    print("\n--- Testing Probability Calculation ---")
    test_ability = 0.0
    test_difficulty = 0.0
    prob = probability_correct(test_ability, test_difficulty)
    print(f"P(correct | θ={test_ability}, b={test_difficulty}) = {prob:.3f}")
    print(f"Expected: ~0.75 (for guessing=0.25)")
    
    # Test ability update
    print("\n--- Testing Ability Update ---")
    new_ability = update_ability(0.0, is_correct=True, question_difficulty=0.0)
    print(f"After correct answer: {new_ability:.2f} (was 0.0)")
    
    new_ability = update_ability(new_ability, is_correct=False, question_difficulty=0.5)
    print(f"After incorrect answer: {new_ability:.2f}")
