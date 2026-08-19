from typing import Dict, Any, List
from backend.models import RecommendationScore, Product, UserProfile, Ritual, Intent

def generate_product_explanation(score: RecommendationScore, product: Product, user_profile: UserProfile) -> Dict[str, Any]:
    matched_concerns = [c for c in user_profile.concerns if c in product.skin_concerns or c in product.tags]
    
    pref_align = []
    for k, v in user_profile.sensory_preferences.items():
        if product.sensory_profile.get(k) == v:
            pref_align.append(f"{v} {k}")
            
    summary = f"Selected {product.name} because it perfectly aligns with your ritual goals."
    if matched_concerns:
        summary = f"Selected because it addresses your focus on {', '.join(matched_concerns)}."
        
    price_note = "Fits perfectly within your stated budget." if score.factors.get("AffordabilityFit", 0) > 0.8 else "A slight investment, but highly relevant."
    
    evidence_note = f"Supported by high-quality evidence ({product.evidence_quality*100:.0f}% confidence)." if product.evidence_quality >= 0.8 else "Based on traditional Ayurvedic practices."
    
    return {
        "summary": summary,
        "matching_needs": matched_concerns,
        "preference_alignment": pref_align,
        "routine_fit": f"Fits perfectly as a {product.routine_stage.value} step.",
        "evidence_note": evidence_note,
        "price_note": price_note,
        "score_breakdown": score.factors
    }

def generate_ritual_explanation(ritual: Ritual, user_profile: UserProfile, intent: Intent) -> str:
    moment_name = ritual.moment.value
    steps_count = ritual.complexity_score
    return f"I've designed a {steps_count}-step {moment_name} ritual for you. This sequence respects your complexity preference and provides a cohesive experience from start to finish."

def generate_alternative_explanation(selected: Product, rejected: Product) -> str:
    return f"We recommended {selected.name} over {rejected.name} because it offers a better match for your stated concerns and fits seamlessly into your requested routine length."
