import json
from backend.models import Intent, RitualPillar
from backend.config import settings

def extract_intent_keyword_fallback(text: str) -> Intent:
    """Legacy keyword-based intent extraction as a fallback.
    Enhanced with Hindi/Hinglish/Marathi keywords for multilingual safety."""
    text = text.lower()
    intent = Intent()
    
    # 1. Detect Medical Risk — multilingual keywords
    medical_keywords = [
        # English
        "rash", "infection", "burn", "bleeding", "severe", "doctor", "pain", "allergic",
        "swelling", "pus", "blisters", "hives",
        # Hindi/Hinglish (romanized)
        "daane", "dane", "jalan", "sujan", "dard", "khujli", "allergi",
        "infection", "pus", "chaale", "phode", "laal", "redness",
        "kharish", "sooj", "soojh",
        # Marathi (romanized)
        "purel", "daah", "vedana", "suj", "khaj",
    ]
    if any(kw in text for kw in medical_keywords):
        intent.medical_risk = True
        intent.confidence_scores["medical_risk"] = 0.9
        return intent # Return early for safety

    # 2. Detect Concerns & Goals — enhanced with Indic terms
    concern_keywords = {
        "dry": ["dry", "flaky", "dehydrated", "tight", "sukhi", "rookhi", "rukha", "hydration", "dryness"],
        "oily": ["oily", "greasy", "shine", "chipchipa", "tel", "acne", "pimple"],
        "sensitive": ["sensitive", "redness", "irritated", "nazuk", "calming", "soothing"],
        "dull": ["dull", "dullness", "lackluster", "brighten", "glow", "niraas", "chamak"],
        "aging": ["aging", "wrinkles", "lines", "fine lines", "mature", "firm", "jhurri"],
        "sleep": ["sleep", "insomnia", "restless", "wake up", "neend", "nind"],
        "stressed": ["stress", "anxious", "overwhelmed", "calm", "relax", "relaxation", "tension", "thaka"],
    }
    
    for concern, keywords in concern_keywords.items():
        if any(kw in text for kw in keywords):
            intent.concerns.append(concern)
            intent.confidence_scores[f"concern_{concern}"] = 0.8

    if "dry" in intent.concerns:
        intent.primary_goal = "skin_hydration"
    elif "dull" in intent.concerns:
        intent.primary_goal = "skin_glow"
    elif "aging" in intent.concerns:
        intent.primary_goal = "anti_aging"
    elif "sensitive" in intent.concerns:
        intent.primary_goal = "barrier_repair"
    elif "stressed" in intent.concerns or "sleep" in intent.concerns:
        intent.primary_goal = "evening_relaxation"
            
    # 3. Detect Ritual Moment — enhanced
    if any(kw in text for kw in ["evening", "night", "bed", "sleep", "wind down", "pm", "raat", "shaam"]):
        intent.routine_time = "evening"
    elif any(kw in text for kw in ["morning", "wake", "start day", "am", "subah", "savere"]):
        intent.routine_time = "morning"
    elif any(kw in text for kw in ["anytime", "any", "daily", "kabhi bhi"]):
        intent.routine_time = "any"

    # 4. Detect Complexity — enhanced
    if any(kw in text for kw in ["simple", "minimal", "quick", "easy", "basic", "uncomplicated", "aasan", "chhota", "1-2 mins", "3-5 mins"]):
        intent.complexity = "simple"
        intent.confidence_scores["complexity"] = 0.85
    elif any(kw in text for kw in ["full", "comprehensive", "complete", "multi-step", "poora", "pura", "10+ mins"]):
        intent.complexity = "comprehensive"

    # 5. Detect Budget
    if any(kw in text for kw in ["affordable", "budget", "cheap", "sasta"]):
        intent.budget = "affordable"
    elif any(kw in text for kw in ["mid-range", "medium", "moderate"]):
        intent.budget = "mid-range"
    elif any(kw in text for kw in ["premium", "luxury", "expensive"]):
        intent.budget = "premium"
        
    # 6. Detect Lifestyle
    if any(kw in text for kw in ["busy", "stressed", "hectic", "work", "kaam", "vyast"]):
        intent.lifestyle = "Busy & Stressed"
    elif any(kw in text for kw in ["active", "outdoors", "sports", "gym", "bahar", "khel"]):
        intent.lifestyle = "Active & Outdoors"
    elif any(kw in text for kw in ["indoors", "home", "desk", "office", "ghar", "andar"]):
        intent.lifestyle = "Mostly Indoors"
    elif any(kw in text for kw in ["relaxed", "chill", "balanced", "easy", "aaram", "shant"]):
        intent.lifestyle = "Relaxed"
        
    return intent

def extract_intent(text: str, current_profile: dict = None) -> Intent:
    """Uses OpenAI LLM to extract structured intent, safety flags, and missing information.
    
    The text passed here should ideally be the NORMALIZED English version
    from the language intelligence layer, ensuring language-independent
    intent extraction quality.
    """
    
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        known_context = ""
        if current_profile:
            known_context = f"Known Profile so far: {json.dumps({k: v for k, v in current_profile.items() if v})}\n"
            
        prompt = f"""
        Extract the user's intent from the following message, considering any known profile details.
        Output ONLY a JSON object matching this schema, with no other text or markdown.
        
        Schema rules:
        - "goals": array of strings (e.g. "skin_hydration", "skin_glow", "evening_relaxation", "repair", "anti_aging")
        - "concerns": array of skin/wellness concerns (e.g. "dry", "dull", "aging", "sensitive", "stressed", "oily")
        - "routine_time": "morning" | "evening" | "any" | null
        - "complexity_preference": "simple" | "comprehensive" | null
        - "budget": "affordable" | "mid-range" | "premium" | null
        - "lifestyle": "Busy & Stressed" | "Active & Outdoors" | "Mostly Indoors" | "Relaxed" | null
        - "constraints": array of strings (e.g. "budget", "no fragrance", "max_2_products")
        - "medical_risk": boolean. True ONLY if the user mentions a medical condition needing diagnosis/treatment (e.g., rash, infection, severe pain, burning, allergic reaction).
        - "request_type": "greeting" | "clarification" | "recommendation" | "product_information". Default to recommendation if asking for help or stating preferences/concerns.
        - "confidence_scores": dict of float 0.0-1.0 mapping the goals to confidence.
        - "product_count": integer or null — If the user explicitly requests a specific number of products, extract it. Otherwise null.
        
        {known_context}
        User Message: "{text}"
        """
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        data = json.loads(content)
        
        # Map to Intent object
        intent = Intent()
        goals = data.get("goals", [])
        if goals:
            intent.primary_goal = goals[0]
            if len(goals) > 1:
                intent.secondary_goal = goals[1]
        
        # Map concerns
        extracted_concerns = data.get("concerns", [])
        for c in extracted_concerns:
            if c not in intent.concerns:
                intent.concerns.append(c)
                
        # Map goals to concerns for backwards compatibility in the pipeline
        for g in goals:
            g_lower = g.lower()
            if ("hydration" in g_lower or "dry" in g_lower) and "dry" not in intent.concerns:
                intent.concerns.append("dry")
            elif ("glow" in g_lower or "bright" in g_lower or "dull" in g_lower) and "dull" not in intent.concerns:
                intent.concerns.append("dull")
            elif ("relax" in g_lower or "sleep" in g_lower or "stress" in g_lower) and "stressed" not in intent.concerns:
                intent.concerns.append("stressed")
            elif ("aging" in g_lower or "wrinkle" in g_lower) and "aging" not in intent.concerns:
                intent.concerns.append("aging")
            elif ("sensitive" in g_lower or "calm" in g_lower or "repair" in g_lower) and "sensitive" not in intent.concerns:
                intent.concerns.append("sensitive")
            
        intent.routine_time = data.get("routine_time")
        intent.complexity = data.get("complexity_preference")
        intent.budget = data.get("budget")
        intent.lifestyle = data.get("lifestyle")
        intent.medical_risk = data.get("medical_risk", False)
        intent.request_type = data.get("request_type", "recommendation")
        intent.confidence_scores = data.get("confidence_scores", {})
        
        # Handle product count constraint
        product_count = data.get("product_count")
        if product_count and isinstance(product_count, int):
            intent.preferences["max_products"] = product_count
            if product_count <= 2:
                intent.complexity = "simple"
        
        return intent
        
    except Exception as e:
        print(f"LLM Intent extraction failed: {e}. Falling back to keywords.")
        return extract_intent_keyword_fallback(text)
