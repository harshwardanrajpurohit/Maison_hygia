from typing import List, Dict, Optional
from backend.models import Product, RitualPillar, RoutineStage, Ritual, RitualStep, UserProfile

RITUAL_TEMPLATES = {
    RitualPillar.GLOW: [
        [RoutineStage.CLEANSE, RoutineStage.MOISTURIZE], # Simple
        [RoutineStage.CLEANSE, RoutineStage.SERUM, RoutineStage.MOISTURIZE], # Medium
        [RoutineStage.CLEANSE, RoutineStage.SERUM, RoutineStage.MOISTURIZE, RoutineStage.TEA] # Comprehensive
    ],
    RitualPillar.PAUSE: [
        [RoutineStage.CLEANSE, RoutineStage.MOISTURIZE], 
        [RoutineStage.CLEANSE, RoutineStage.TREAT, RoutineStage.MOISTURIZE],
        [RoutineStage.TEA, RoutineStage.CLEANSE, RoutineStage.TREAT, RoutineStage.MOISTURIZE]
    ],
    RitualPillar.NOURISH: [
        [RoutineStage.SNACK, RoutineStage.TEA],
        [RoutineStage.SNACK, RoutineStage.TEA, RoutineStage.SUPPLEMENT],
        [RoutineStage.SNACK, RoutineStage.SNACK, RoutineStage.TEA]
    ],
    RitualPillar.CARE: [
        [RoutineStage.CLEANSE, RoutineStage.MOISTURIZE],
        [RoutineStage.CLEANSE, RoutineStage.TREAT, RoutineStage.MOISTURIZE],
        [RoutineStage.CLEANSE, RoutineStage.TREAT, RoutineStage.MOISTURIZE, RoutineStage.SUPPLEMENT]
    ],
    RitualPillar.GATHER: [
        [RoutineStage.SNACK, RoutineStage.SNACK],
        [RoutineStage.SNACK, RoutineStage.SNACK, RoutineStage.TEA],
        [RoutineStage.SNACK, RoutineStage.SNACK, RoutineStage.TEA, RoutineStage.TEA]
    ]
}

def determine_complexity_index(complexity: str) -> int:
    if complexity == "simple": return 0
    if complexity == "comprehensive": return 2
    return 1 # medium by default

def compose_ritual(ranked_products: List[Product], moment: RitualPillar, user_profile: UserProfile) -> Optional[Ritual]:
    if not ranked_products:
        return None
        
    complexity = user_profile.complexity_tolerance or "medium"
    comp_idx = determine_complexity_index(complexity)
    
    # Fallback to GLOW if unknown
    if moment not in RITUAL_TEMPLATES:
        moment = RitualPillar.GLOW
        
    template = RITUAL_TEMPLATES[moment][comp_idx]
    
    steps = []
    used_product_ids = set()
    total_price = 0.0
    
    for i, stage in enumerate(template):
        # Find best product for this stage
        selected_prod = None
        for prod in ranked_products:
            if prod.routine_stage == stage and prod.id not in used_product_ids:
                selected_prod = prod
                break
                
        # If no strict match, find closest alternative or skip
        if not selected_prod:
            for prod in ranked_products:
                if prod.id not in used_product_ids:
                    selected_prod = prod
                    break
                    
        if selected_prod:
            used_product_ids.add(selected_prod.id)
            steps.append(RitualStep(
                step_number=i+1,
                stage_name=stage.value.capitalize(),
                product=selected_prod
            ))
            total_price += selected_prod.price
            
    if not steps:
        return None
        
    return Ritual(
        moment=moment,
        steps=steps,
        total_price=total_price,
        complexity_score=len(steps)
    )
