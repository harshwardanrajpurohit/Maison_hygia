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

    # 2. Detect Concerns — enhanced with Indic terms
    concern_keywords = {
        "dry": ["dry", "flaky", "dehydrated", "tight", "sukhi", "rookhi", "rukha"],
        "oily": ["oily", "greasy", "shine", "oily", "chipchipa", "tel"],
        "sensitive": ["sensitive", "redness", "irritated", "nazuk"],
        "dull": ["dull", "lackluster", "brighten", "glow", "niraas", "chamak"],
        "aging": ["aging", "wrinkles", "lines", "mature", "firm", "jhurri"],
        "sleep": ["sleep", "insomnia", "restless", "wake up", "neend", "nind"],
        "stress": ["stress", "anxious", "overwhelmed", "calm", "relax", "tension", "thaka"],
    }
    
    for concern, keywords in concern_keywords.items():
        if any(kw in text for kw in keywords):
            intent.concerns.append(concern)
            intent.confidence_scores[f"concern_{concern}"] = 0.8
            
    # 3. Detect Ritual Moment — enhanced
    if any(kw in text for kw in ["evening", "night", "bed", "sleep", "wind down", "pm", "raat", "shaam"]):
        intent.routine_time = "evening"
    elif any(kw in text for kw in ["morning", "wake", "start day", "am", "subah", "savere"]):
        intent.routine_time = "morning"

    # 4. Detect Complexity — enhanced
    if any(kw in text for kw in ["simple", "minimal", "quick", "easy", "basic", "uncomplicated", "aasan", "chhota"]):
        intent.complexity = "simple"
        intent.confidence_scores["complexity"] = 0.85
    elif any(kw in text for kw in ["full", "comprehensive", "complete", "multi-step", "poora", "pura"]):
        intent.complexity = "comprehensive"
        
    # Check for missing info (only if it's a recommendation request)
    if intent.request_type == "recommendation":
        if not intent.routine_time:
            intent.missing_information.append("routine_time")
        if not intent.complexity:
            intent.missing_information.append("complexity")

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
            
        prompt = f"""
        Extract the user's intent from the following text.
        Output ONLY a JSON object matching this schema, with no other text or markdown.
        
        Schema rules:
        - "goals": array of strings (e.g. "skin_hydration", "evening_relaxation", "repair")
        - "routine_time": "morning" | "evening" | "any" | null
        - "complexity_preference": "simple" | "comprehensive" | null
        - "budget": "affordable" | "mid-range" | "premium" | null
        - "constraints": array of strings (e.g. "budget", "no fragrance", "max_2_products")
        - "medical_risk": boolean. True ONLY if the user mentions a medical condition needing diagnosis/treatment (e.g., rash, infection, severe pain, burning, allergic reaction).
        - "request_type": "greeting" | "clarification" | "recommendation" | "product_information". Default to recommendation if asking for help.
        - "missing_information": array of strings listing critical info missing to build a routine (e.g. "routine_time", "complexity_preference"). Do NOT list them if the user already provided them. Do NOT list them if the request_type is greeting or clarification.
        - "confidence_scores": dict of float 0.0-1.0 mapping the goals to confidence.
        - "product_count": integer or null — If the user explicitly requests a specific number of products, extract it. Otherwise null.
        
        Text: "{text}"
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
        
        # Map goals to concerns for backwards compatibility in the pipeline
        for g in goals:
            if "hydration" in g or "dry" in g: intent.concerns.append("dry")
            elif "relax" in g or "sleep" in g: intent.concerns.append("stressed")
            
        intent.routine_time = data.get("routine_time")
        intent.complexity = data.get("complexity_preference")
        intent.budget = data.get("budget")
        intent.medical_risk = data.get("medical_risk", False)
        intent.request_type = data.get("request_type", "recommendation")
        intent.missing_information = data.get("missing_information", [])
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
