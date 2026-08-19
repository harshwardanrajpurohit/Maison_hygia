from typing import List, Tuple, Dict
from backend.models import Product, UserProfile, Ritual, RitualStep

def score_product(product: Product, user_profile: UserProfile, weights: Dict[str, float] = None) -> Tuple[float, Dict[str, float]]:
    """
    Scores a product against a user profile. 
    In the new case study architecture, Consumer Relevance heavily dominates Business Value.
    """
    if weights is None:
        weights = {
            "need_match": 0.40,
            "routine_fit": 0.15,
            "preference_match": 0.20,
            "ingredient_match": 0.10,
            "simplicity": 0.10,
            "business_value": 0.05
        }

    # 1. Need Match (Does it solve their concerns?)
    need_match = 0.0
    matched_concerns = set(product.skin_concerns).intersection(set(user_profile.concerns))
    if matched_concerns:
        need_match = len(matched_concerns) / len(user_profile.concerns) if user_profile.concerns else 0.0
    
    if user_profile.primary_goal in product.wellness_goals:
        need_match += 0.5
    if user_profile.secondary_goal in product.wellness_goals:
        need_match += 0.2
    need_match = min(1.0, need_match)

    # 2. Routine Fit (Does it fit the time of day?)
    routine_fit = 0.0
    pref_time = user_profile.preferred_routine_time or "any"
    if product.routine_time == "any" or product.routine_time == pref_time:
        routine_fit = 1.0

    # 3. Preference / Memory Match
    pref_match = 0.5 # Baseline
    if product.id in user_profile.liked_products:
        pref_match = 1.0
    if product.id in user_profile.disliked_products:
        pref_match = 0.0

    # 4. Ingredient / Evidence Match
    ingredient_match = product.evidence_quality

    # 5. Simplicity (Fewer tags/complex instructions = simpler)
    simplicity = 1.0 if "simple" in product.tags else 0.5

    # 6. Business Value (Margin)
    business_value = {"low": 0.3, "medium": 0.6, "high": 1.0}.get(product.margin, 0.5)

    # Calculate final score
    factors = {
        "Need Match": need_match,
        "Routine Fit": routine_fit,
        "Simplicity": simplicity,
        "Business Value": business_value
    }
    
    total_score = (
        need_match * weights["need_match"] +
        routine_fit * weights["routine_fit"] +
        pref_match * weights["preference_match"] +
        ingredient_match * weights["ingredient_match"] +
        simplicity * weights["simplicity"] +
        business_value * weights["business_value"]
    )

    # 7. Budget / Margin match
    if user_profile.budget:
        budget_lower = user_profile.budget.lower()
        budget_map = {
            "affordable": "low", "affordable ($)": "low",
            "mid-range": "medium", "mid-range ($$)": "medium",
            "premium": "high", "premium ($$$)": "high"
        }
        target_margin = budget_map.get(budget_lower)
        
        if target_margin:
            if product.margin == target_margin:
                pref_match += 0.5 # Boost exact matches
            elif target_margin == "low" and product.margin == "high":
                pref_match = 0.0 # Strict penalty for premium when affordable requested

    # Hard constraints: If they disliked it, don't recommend it.
    if pref_match == 0.0:
        total_score = 0.0

    return total_score, factors

def generate_why_explanation(product: Product, user_profile: UserProfile, factors: Dict[str, float]) -> str:
    # Conversational, human explanations
    if factors["Need Match"] > 0 and user_profile.primary_goal in product.wellness_goals:
        goal_name = user_profile.primary_goal.replace('_', ' ')
        return f"Picked because {goal_name} is your main focus right now."
        
    if factors["Routine Fit"] == 1.0 and user_profile.preferred_routine_time:
        return f"A great match for a {user_profile.preferred_routine_time} routine."
        
    if "simple" in product.tags and user_profile.complexity_tolerance == "simple":
        return "Included this to keep things easy and quick."
        
    return "Selected because it fits well with what you're looking for."

def build_ritual(user_profile: UserProfile, all_products: List[Product]) -> Ritual:
    """Selects the top products and formats them into a structured Ritual."""
    
    # Target steps based on complexity or explicit max
    if user_profile.max_products:
        target_steps = user_profile.max_products
    else:
        target_steps = 2 if user_profile.complexity_tolerance == "simple" else 3
    
    scored = []
    for p in all_products:
        score, factors = score_product(p, user_profile)
        if score > 0.2: # Relevance threshold
            scored.append((score, p, factors))
            
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # We want a logical flow: prepare -> treat -> moisturize/wind_down
    # This is simplified for the prototype
    ritual_steps = []
    total_price = 0.0
    step_num = 1
    
    # Take the best products up to target_steps
    for score, product, factors in scored:
        if len(ritual_steps) >= target_steps:
            break
            
        why_text = generate_why_explanation(product, user_profile, factors)
        
        rs = RitualStep(
            step_number=step_num,
            stage_name=product.routine_stage,
            product=product,
            why_selected=why_text
        )
        ritual_steps.append(rs)
        total_price += product.price
        step_num += 1

    # Sort steps logically (cleanse first)
    stage_order = {"cleanse": 1, "prepare": 2, "treat": 3, "moisturize": 4, "wind_down": 5}
    ritual_steps.sort(key=lambda x: stage_order.get(x.stage_name, 99))
    
    # Fix step numbers after sorting
    for i, step in enumerate(ritual_steps):
        step.step_number = i + 1

    why_this_ritual = [
        f"{len(ritual_steps)} steps to keep it manageable",
        f"Focused on your {user_profile.primary_goal.replace('_', ' ') if user_profile.primary_goal else 'wellness'} goal",
    ]

    return Ritual(
        moment=user_profile.preferred_routine_time or "Tailored",
        steps=ritual_steps,
        total_price=total_price,
        why_this_ritual=why_this_ritual
    )
