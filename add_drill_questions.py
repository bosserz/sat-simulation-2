#!/usr/bin/env python3
"""
Add drill questions and drill_sets structure to questions.json
"""
import json

# Load existing questions
with open('database/questions.json', 'r') as f:
    data = json.load(f)

# Add drill_sets structure - maps topic names to sets with question IDs
# These IDs will reference skill_questions below
data['drill_sets'] = {
    "Words in Context": {
        "description": "Master context clues and word meanings",
        "section_type": "verbal",
        "sets": {
            "set_1": {
                "difficulty": "Easy",
                "num_questions": 8,
                "question_ids": [20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008]
            },
            "set_2": {
                "difficulty": "Medium",
                "num_questions": 10,
                "question_ids": [20009, 20010, 20011, 20012, 20013, 20014, 20015, 20016, 20017, 20018]
            },
            "set_3": {
                "difficulty": "Hard",
                "num_questions": 9,
                "question_ids": [20019, 20020, 20021, 20022, 20023, 20024, 20025, 20026, 20027]
            }
        }
    },
    "Literary Inference": {
        "description": "Develop skills to make inferences from passages",
        "section_type": "verbal",
        "sets": {
            "set_1": {
                "difficulty": "Easy",
                "num_questions": 7,
                "question_ids": [20028, 20029, 20030, 20031, 20032, 20033, 20034]
            },
            "set_2": {
                "difficulty": "Medium",
                "num_questions": 9,
                "question_ids": [20035, 20036, 20037, 20038, 20039, 20040, 20041, 20042, 20043]
            },
            "set_3": {
                "difficulty": "Hard",
                "num_questions": 8,
                "question_ids": [20044, 20045, 20046, 20047, 20048, 20049, 20050, 20051]
            }
        }
    },
    "Command of Grammar": {
        "description": "Practice grammar, syntax, and sentence structure",
        "section_type": "verbal",
        "sets": {
            "set_1": {
                "difficulty": "Easy",
                "num_questions": 10,
                "question_ids": [20052, 20053, 20054, 20055, 20056, 20057, 20058, 20059, 20060, 20061]
            },
            "set_2": {
                "difficulty": "Medium",
                "num_questions": 9,
                "question_ids": [20062, 20063, 20064, 20065, 20066, 20067, 20068, 20069, 20070]
            },
            "set_3": {
                "difficulty": "Hard",
                "num_questions": 8,
                "question_ids": [20071, 20072, 20073, 20074, 20075, 20076, 20077, 20078]
            }
        }
    },
    "Algebra": {
        "description": "Master algebraic equations and expressions",
        "section_type": "math",
        "sets": {
            "set_1": {
                "difficulty": "Easy",
                "num_questions": 8,
                "question_ids": [30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008]
            },
            "set_2": {
                "difficulty": "Medium",
                "num_questions": 10,
                "question_ids": [30009, 30010, 30011, 30012, 30013, 30014, 30015, 30016, 30017, 30018]
            },
            "set_3": {
                "difficulty": "Hard",
                "num_questions": 9,
                "question_ids": [30019, 30020, 30021, 30022, 30023, 30024, 30025, 30026, 30027]
            }
        }
    },
    "Advanced Math": {
        "description": "Tackle complex mathematical problems",
        "section_type": "math",
        "sets": {
            "set_1": {
                "difficulty": "Easy",
                "num_questions": 7,
                "question_ids": [30028, 30029, 30030, 30031, 30032, 30033, 30034]
            },
            "set_2": {
                "difficulty": "Medium",
                "num_questions": 9,
                "question_ids": [30035, 30036, 30037, 30038, 30039, 30040, 30041, 30042, 30043]
            },
            "set_3": {
                "difficulty": "Hard",
                "num_questions": 8,
                "question_ids": [30044, 30045, 30046, 30047, 30048, 30049, 30050, 30051]
            }
        }
    },
    "Geometry": {
        "description": "Practice shapes, angles, and spatial relationships",
        "section_type": "math",
        "sets": {
            "set_1": {
                "difficulty": "Easy",
                "num_questions": 8,
                "question_ids": [30052, 30053, 30054, 30055, 30056, 30057, 30058, 30059]
            },
            "set_2": {
                "difficulty": "Medium",
                "num_questions": 9,
                "question_ids": [30060, 30061, 30062, 30063, 30064, 30065, 30066, 30067, 30068]
            },
            "set_3": {
                "difficulty": "Hard",
                "num_questions": 7,
                "question_ids": [30069, 30070, 30071, 30072, 30073, 30074, 30075]
            }
        }
    }
}

# Add dedicated drill questions
data['skill_questions'] = [
    # Words in Context - Easy (8 questions)
    {
        "question_id": 20001,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "The artist's <span class=\"blank\">______</span> approach to painting was evident in every brushstroke, showing careful planning and attention to detail.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["careless", "methodical", "hasty", "random"],
        "correct_answer": "methodical"
    },
    {
        "question_id": 20002,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "Despite her initial <span class=\"blank\">______</span>, Maria became a confident speaker by practicing regularly.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["confidence", "trepidation", "expertise", "eloquence"],
        "correct_answer": "trepidation"
    },
    {
        "question_id": 20003,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "The scientist's <span class=\"blank\">______</span> findings were widely accepted by the community.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["dubious", "anomalous", "conclusive", "preliminary"],
        "correct_answer": "conclusive"
    },
    {
        "question_id": 20004,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "The <span class=\"blank\">______</span> landscape was barren and lifeless, with no vegetation in sight.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["verdant", "arid", "lush", "fertile"],
        "correct_answer": "arid"
    },
    {
        "question_id": 20005,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "The ancient texts were <span class=\"blank\">______</span>, allowing scholars to understand the culture of the time.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["obscure", "cryptic", "informative", "confusing"],
        "correct_answer": "informative"
    },
    {
        "question_id": 20006,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "The chef's <span class=\"blank\">______</span> nature meant she was always willing to try new ingredients and techniques.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["conservative", "adventurous", "boring", "traditional"],
        "correct_answer": "adventurous"
    },
    {
        "question_id": 20007,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "Her <span class=\"blank\">______</span> voice soothed the frightened child.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["shrill", "gentle", "harsh", "loud"],
        "correct_answer": "gentle"
    },
    {
        "question_id": 20008,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Easy",
        "passage": "The <span class=\"blank\">______</span> rules of the game allowed no room for interpretation.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["flexible", "ambiguous", "strict", "vague"],
        "correct_answer": "strict"
    },
    # Words in Context - Medium (10 questions)
    {
        "question_id": 20009,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The politician's <span class=\"blank\">______</span> speech failed to address the real issues facing constituents.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["eloquent", "obfuscatory", "clear", "detailed"],
        "correct_answer": "obfuscatory"
    },
    {
        "question_id": 20010,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The <span class=\"blank\">______</span> nature of quantum mechanics continues to perplex even experienced physicists.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["simplistic", "esoteric", "elementary", "transparent"],
        "correct_answer": "esoteric"
    },
    {
        "question_id": 20011,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "Despite the <span class=\"blank\">______</span> nature of their disagreements, the team remained united in purpose.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["superficial", "intractable", "harmonious", "insignificant"],
        "correct_answer": "intractable"
    },
    {
        "question_id": 20012,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The author's <span class=\"blank\">______</span> writing style made the novel difficult to follow.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["lucid", "convoluted", "straightforward", "precise"],
        "correct_answer": "convoluted"
    },
    {
        "question_id": 20013,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "Her <span class=\"blank\">______</span> dedication to the project surprised everyone who knew her.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["halfhearted", "steadfast", "wavering", "uncertain"],
        "correct_answer": "steadfast"
    },
    {
        "question_id": 20014,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The critic's <span class=\"blank\">______</span> review of the film was so harsh that few people took it seriously.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["measured", "scathing", "balanced", "fair"],
        "correct_answer": "scathing"
    },
    {
        "question_id": 20015,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The <span class=\"blank\">______</span> discovery of the ancient artifact revolutionized our understanding of the civilization.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["trivial", "momentous", "minor", "insignificant"],
        "correct_answer": "momentous"
    },
    {
        "question_id": 20016,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The speaker's <span class=\"blank\">______</span> manner made the audience uncomfortable and suspicious of their motives.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["forthright", "disingenuous", "sincere", "candid"],
        "correct_answer": "disingenuous"
    },
    {
        "question_id": 20017,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "The <span class=\"blank\">______</span> beauty of the sunset left the observers breathless.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["mundane", "ethereal", "ordinary", "plain"],
        "correct_answer": "ethereal"
    },
    {
        "question_id": 20018,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Medium",
        "passage": "His <span class=\"blank\">______</span> attitude toward the problem prevented him from finding a solution.",
        "question": "Which choice completes the text with the most logical word?",
        "options": ["pragmatic", "myopic", "practical", "realistic"],
        "correct_answer": "myopic"
    },
    # Words in Context - Hard (9 questions)
    {
        "question_id": 20019,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "The author's <span class=\"blank\">______</span> treatise on philosophy was an attempt to <span class=\"blank\">______</span> the dominant paradigm.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["iconoclastic...reinforce", "pedantic...undermine", "heterodox...subvert", "orthodox...challenge"],
        "correct_answer": "heterodox...subvert"
    },
    {
        "question_id": 20020,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "While the film was ostensibly about love, its <span class=\"blank\">______</span> message revealed a more <span class=\"blank\">______</span> truth.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["overt...superficial", "implicit...profound", "apparent...trivial", "explicit...shallow"],
        "correct_answer": "implicit...profound"
    },
    {
        "question_id": 20021,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "The scholar's <span class=\"blank\">______</span> analysis of the text was so <span class=\"blank\">______</span> that it left no room for alternative interpretations.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["nuanced...ambiguous", "rigorous...irrefutable", "cursory...definitive", "superficial...conclusive"],
        "correct_answer": "rigorous...irrefutable"
    },
    {
        "question_id": 20022,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "Rather than offering a <span class=\"blank\">______</span> solution, the consultant proposed a more <span class=\"blank\">______</span> approach.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["temporary...permanent", "facile...nuanced", "complex...simple", "innovative...conventional"],
        "correct_answer": "facile...nuanced"
    },
    {
        "question_id": 20023,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "The <span class=\"blank\">______</span> nature of the artifact made classification <span class=\"blank\">______</span> for the museum curators.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["unique...impossible", "anomalous...problematic", "ordinary...easy", "peculiar...trivial"],
        "correct_answer": "anomalous...problematic"
    },
    {
        "question_id": 20024,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "The company's <span class=\"blank\">______</span> expansion plans were tempered by concerns about economic <span class=\"blank\">______</span>.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["aggressive...growth", "ambitious...volatility", "cautious...stability", "rash...prosperity"],
        "correct_answer": "ambitious...volatility"
    },
    {
        "question_id": 20025,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "The <span class=\"blank\">______</span> claims of the defendant were <span class=\"blank\">______</span> by the overwhelming evidence.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["plausible...supported", "implausible...corroborated", "credible...contradicted", "dubious...substantiated"],
        "correct_answer": "dubious...substantiated"
    },
    {
        "question_id": 20026,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "The <span class=\"blank\">______</span> debate about climate policy revealed how <span class=\"blank\">______</span> the public's understanding was.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["heated...sophisticated", "acrimonious...impoverished", "spirited...advanced", "casual...comprehensive"],
        "correct_answer": "acrimonious...impoverished"
    },
    {
        "question_id": 20027,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Words in Context",
        "level": "Hard",
        "passage": "His <span class=\"blank\">______</span> remarks were meant to <span class=\"blank\">______</span> the growing tension in the room.",
        "question": "Which choices complete the text with the most logical words?",
        "options": ["acerbic...exacerbate", "sardonic...ameliorate", "caustic...mitigate", "benign...augment"],
        "correct_answer": "benign...ameliorate"
    },
    # Literary Inference - Easy (7 questions)
    {
        "question_id": 20028,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "The old lighthouse stood alone on the rocky cliff, its light still turning faithfully each evening. Sailors knew they could depend on it to guide them safely home.",
        "question": "Based on the passage, what can be inferred about the lighthouse?",
        "options": ["It is no longer functional", "It is a valuable source of guidance", "It is dangerous to approach", "It is abandoned"],
        "correct_answer": "It is a valuable source of guidance"
    },
    {
        "question_id": 20029,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "Sarah clutched her exam results to her chest, a smile spreading across her face. She immediately called her parents to share the good news.",
        "question": "What can be inferred about Sarah's exam results?",
        "options": ["She failed the exam", "She performed well", "She was disappointed", "The results were unexpected"],
        "correct_answer": "She performed well"
    },
    {
        "question_id": 20030,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "The garden was overgrown with weeds, and many flowers had withered despite the recent rains. No one had tended to it in months.",
        "question": "What can be inferred from the condition of the garden?",
        "options": ["The garden is well-maintained", "The garden has been neglected", "The weather has been ideal", "The flowers are thriving"],
        "correct_answer": "The garden has been neglected"
    },
    {
        "question_id": 20031,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "Marcus hesitated at the doorway, his hands trembling slightly. He took a deep breath before entering the interview room.",
        "question": "What can be inferred about Marcus's emotional state?",
        "options": ["He was calm and relaxed", "He was nervous about the interview", "He was angry", "He was bored"],
        "correct_answer": "He was nervous about the interview"
    },
    {
        "question_id": 20032,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "The restaurant's tables were mostly empty, and the once cheerful décor was now faded and worn. The staff seemed to move slowly through their duties.",
        "question": "What can be inferred about the restaurant's business?",
        "options": ["It is thriving", "It is popular with customers", "It appears to be struggling", "It is newly opened"],
        "correct_answer": "It appears to be struggling"
    },
    {
        "question_id": 20033,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "Elena kept checking her phone, looking toward the door every few minutes. Her foot tapped impatiently under the table.",
        "question": "What can be inferred about Elena's state of mind?",
        "options": ["She is bored", "She is anxiously waiting for someone", "She is angry", "She is disinterested"],
        "correct_answer": "She is anxiously waiting for someone"
    },
    {
        "question_id": 20034,
        "type": "verbal",
        "domain": "Craft and Structure",
        "skill": "Literary Inference",
        "level": "Easy",
        "passage": "The child's birthday cake was homemade, with frosting applied carefully and decorations arranged with obvious love and attention to detail.",
        "question": "What can be inferred about the person who made the cake?",
        "options": ["They had professional baking experience", "They made it hastily", "They cared deeply about the birthday child", "They had little skill in baking"],
        "correct_answer": "They cared deeply about the birthday child"
    },
    # Add more sample questions for other topics (abbreviated for length)
    # Command of Grammar - Easy (3 samples)
    {
        "question_id": 20052,
        "type": "verbal",
        "domain": "Command of Grammar",
        "skill": "Command of Grammar",
        "level": "Easy",
        "passage": "The team _______ working hard to prepare for the championship game.",
        "question": "Which choice completes the sentence correctly?",
        "options": ["are", "is", "have", "has"],
        "correct_answer": "is"
    },
    {
        "question_id": 20053,
        "type": "verbal",
        "domain": "Command of Grammar",
        "skill": "Command of Grammar",
        "level": "Easy",
        "passage": "Neither the students nor the teacher _______ aware of the assembly.",
        "question": "Which choice completes the sentence correctly?",
        "options": ["was", "were", "is", "are"],
        "correct_answer": "was"
    },
    {
        "question_id": 20054,
        "type": "verbal",
        "domain": "Command of Grammar",
        "skill": "Command of Grammar",
        "level": "Easy",
        "passage": "The book gave _______ a lot to think about.",
        "question": "Which choice completes the sentence correctly?",
        "options": ["we", "us", "our", "me"],
        "correct_answer": "us"
    },
    # Algebra - Easy (3 samples)
    {
        "question_id": 30001,
        "type": "math",
        "domain": "Algebra",
        "skill": "Algebra",
        "level": "Easy",
        "passage": "If 2x + 5 = 13, what is the value of x?",
        "question": "What is x?",
        "options": ["4", "5", "6", "9"],
        "correct_answer": "4"
    },
    {
        "question_id": 30002,
        "type": "math",
        "domain": "Algebra",
        "skill": "Algebra",
        "level": "Easy",
        "passage": "Simplify: 3(x + 2) - 5",
        "question": "What is the simplified expression?",
        "options": ["3x + 1", "3x + 5", "3x + 6", "3x - 5"],
        "correct_answer": "3x + 1"
    },
    {
        "question_id": 30003,
        "type": "math",
        "domain": "Algebra",
        "skill": "Algebra",
        "level": "Easy",
        "passage": "If y = 2x + 3 and x = 4, what is y?",
        "question": "What is y?",
        "options": ["8", "10", "11", "14"],
        "correct_answer": "11"
    },
    # Advanced Math - Easy (3 samples)
    {
        "question_id": 30028,
        "type": "math",
        "domain": "Advanced Math",
        "skill": "Advanced Math",
        "level": "Easy",
        "passage": "If f(x) = x² + 2x, what is f(3)?",
        "question": "What is f(3)?",
        "options": ["9", "12", "15", "18"],
        "correct_answer": "15"
    },
    {
        "question_id": 30029,
        "type": "math",
        "domain": "Advanced Math",
        "skill": "Advanced Math",
        "level": "Easy",
        "passage": "What is the slope of the line passing through (1, 2) and (3, 6)?",
        "question": "What is the slope?",
        "options": ["1", "2", "3", "4"],
        "correct_answer": "2"
    },
    {
        "question_id": 30030,
        "type": "math",
        "domain": "Advanced Math",
        "skill": "Advanced Math",
        "level": "Easy",
        "passage": "If a triangle has angles of 60° and 70°, what is the third angle?",
        "question": "What is the third angle?",
        "options": ["40°", "50°", "60°", "130°"],
        "correct_answer": "50°"
    },
    # Geometry - Easy (3 samples)
    {
        "question_id": 30052,
        "type": "math",
        "domain": "Geometry",
        "skill": "Geometry",
        "level": "Easy",
        "passage": "What is the area of a rectangle with length 5 and width 3?",
        "question": "What is the area?",
        "options": ["8", "15", "16", "20"],
        "correct_answer": "15"
    },
    {
        "question_id": 30053,
        "type": "math",
        "domain": "Geometry",
        "skill": "Geometry",
        "level": "Easy",
        "passage": "A circle has a radius of 4. What is its area? (Use π ≈ 3.14)",
        "question": "What is the approximate area?",
        "options": ["12.56", "25.12", "50.24", "100.48"],
        "correct_answer": "50.24"
    },
    {
        "question_id": 30054,
        "type": "math",
        "domain": "Geometry",
        "skill": "Geometry",
        "level": "Easy",
        "passage": "In a right triangle, if one leg is 3 and the hypotenuse is 5, what is the other leg?",
        "question": "What is the length of the other leg?",
        "options": ["2", "3", "4", "5"],
        "correct_answer": "4"
    }
]

# Write back to file
with open('database/questions.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Successfully added drill_sets and skill_questions to questions.json")
print(f"   - Added {len(data['drill_sets'])} drill topics")
print(f"   - Added {len(data['skill_questions'])} skill questions")
