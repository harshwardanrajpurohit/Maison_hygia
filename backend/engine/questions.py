import math
from typing import List, Dict, Tuple
from backend.models import Question, UserProfile, Intent

QUESTIONS_DB = [
    Question(
        id="q_goal",
        text="What is your main skin concern or wellness goal?",
        options=["Dryness & Hydration", "Dullness & Glow", "Fine lines & Aging", "Sensitivity & Calming", "Sleep & Relaxation"],
        dimension="primary_goal"
    ),
    Question(
        id="q_moment",
        text="When do you want to do this?",
        options=["Morning", "Evening", "Anytime"],
        dimension="routine_time"
    ),
    Question(
        id="q_complexity",
        text="How much time do you have for your routine?",
        options=["Quick — 1-2 mins", "A bit of self-care — 3-5 mins", "Full ritual — 10+ mins"],
        dimension="complexity"
    ),
    Question(
        id="q_budget",
        text="What's your budget for this?",
        options=["Affordable ($)", "Mid-range ($$)", "Premium ($$$)"],
        dimension="budget"
    ),
    Question(
        id="q_fragrance",
        text="Any fragrance preference?",
        options=["No fragrance", "Light, natural scents", "Rich, sensory experience"],
        dimension="fragrance_level"
    ),
    Question(
        id="q_focus",
        text="Are you looking for skincare, nutrition, or both?",
        options=["Skincare", "Nutrition / Snacks", "Both"],
        dimension="category"
    ),
    Question(
        id="q_lifestyle",
        text="What best describes your current lifestyle or situation?",
        options=["Busy & Stressed", "Active & Outdoors", "Mostly Indoors", "Relaxed"],
        dimension="lifestyle"
    )
]

def calculate_entropy(probabilities: List[float]) -> float:
    return -sum(p * math.log2(p) for p in probabilities if p > 0)

def select_questions(intent: Intent, user_profile: UserProfile, top_n: int = 1) -> List[Question]:
    scored_questions = []
    
    # Determine what we already know to avoid asking redundant questions
    resolved_dims = set()
    if intent.primary_goal or user_profile.primary_goal or user_profile.concerns or intent.concerns:
        resolved_dims.add("primary_goal")
    if intent.budget or user_profile.budget:
        resolved_dims.add("budget")
    if intent.complexity or user_profile.complexity_tolerance:
        resolved_dims.add("complexity")
    if intent.routine_time or user_profile.preferred_routine_time or user_profile.ritual_moment:
        resolved_dims.add("routine_time")
        resolved_dims.add("ritual_moment")
    if "fragrance_level" in intent.preferences or (user_profile.sensory_preferences and "fragrance_level" in user_profile.sensory_preferences): 
        resolved_dims.add("fragrance_level")
    if intent.category_preference:
        resolved_dims.add("category")
    if intent.lifestyle or user_profile.lifestyle:
        resolved_dims.add("lifestyle")
    
    for q in QUESTIONS_DB:
        if q.dimension in resolved_dims:
            continue
            
        # Calculate Information Gain (simplified math model for the prototype)
        # Assuming equal priors for options if unknown
        num_options = len(q.options)
        prior_entropy = calculate_entropy([1.0 / num_options] * num_options)
        
        # Expected posterior entropy is lower because asking the question resolves it
        posterior_entropy = 0.1  # small residual uncertainty
        
        info_gain = prior_entropy - posterior_entropy
        
        # Calculate utility: InfoGain - lambda * UserEffort (effort approx 1.0 for multiple choice)
        lambda_effort = 0.2
        utility = info_gain - lambda_effort * 1.0
        
        # Hardcoded priorities to enforce conversational flow
        if q.dimension == "primary_goal":
            utility += 8.0 # Highest priority if goal/concern is missing
        elif q.dimension in ("routine_time", "ritual_moment"):
            utility += 5.0 # Second highest priority
        elif q.dimension == "complexity":
            utility += 4.0 # Third highest priority
        elif q.dimension == "budget":
            utility -= 2.0 # Deprioritize budget
        elif q.dimension == "lifestyle":
            utility += 3.0 # Important context, but after goal/time
            
        q_copy = q.copy()
        q_copy.information_gain_score = utility
        scored_questions.append(q_copy)
        
    scored_questions.sort(key=lambda x: x.information_gain_score, reverse=True)
    return scored_questions[:top_n]
