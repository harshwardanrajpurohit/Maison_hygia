from pydantic import BaseModel
from typing import Optional
from backend.models import LanguageContext

class SafetyCheckResult(BaseModel):
    status: str
    message: str

# Multilingual medical/safety keywords
# These work on the RAW user input (before normalization) to catch safety
# concerns regardless of language detection success
MEDICAL_KEYWORDS_MULTILINGUAL = [
    # English
    "rash", "infection", "burn", "bleeding", "severe", "doctor", "pain",
    "allergic", "swelling", "pus", "blisters", "hives", "emergency",
    "hospital", "severe pain",
    # Hindi/Hinglish (romanized)
    "rash", "daane", "dane", "jalan", "sujan", "dard", "khujli",
    "allergi", "chaale", "phode", "kharish", "sooj", "soojh",
    "lal dhabbe", "chehra jal", "jal raha",
    # Marathi (romanized)
    "purel", "daah", "vedana", "suj", "khaj", "rash ala",
    # Tamil (romanized)
    "alerji", "vali", "erittal",
    # Bengali (romanized)
    "fola", "bedona", "chulkani",
]

def should_escalate(message: str) -> bool:
    """Medical escalation check — works across languages.
    
    Checks the RAW user message (not normalized) so that
    safety detection is language-independent.
    """
    message_lower = message.lower()
    
    # Check multi-word phrases first
    multi_word = ["severe pain", "lal dhabbe", "chehra jal", "rash ala"]
    if any(phrase in message_lower for phrase in multi_word):
        return True
    
    # Check individual keywords
    high_risk_keywords = [
        "doctor", "hospital", "bleeding", "emergency",
        "severe", "pus", "blisters"
    ]
    return any(term in message_lower for term in high_risk_keywords)

def get_escalation_response() -> str:
    """Legacy escalation response."""
    return "This sounds like a medical emergency. Please contact a healthcare professional or emergency services immediately."

def get_medical_risk_response(language_context: Optional[LanguageContext] = None) -> str:
    """Safety guardrail response — adapts to user's language.
    
    Provides the safety message in the user's detected language
    while keeping it simple and clear.
    """
    lang = "english"
    if language_context:
        lang = language_context.detected_language
    
    if lang in ("hindi", "hinglish"):
        return (
            "Main rash ya skin reaction ka karan nahi bata sakti, aur na hi koi cosmetic product "
            "treatment ke taur pe suggest kar sakti hoon.\n\n"
            "Skin reactions ke alag-alag karan ho sakte hain, isliye kisi doctor ya dermatologist "
            "se baat karna best hoga — especially agar yeh badh raha hai, dard ho raha hai, ya "
            "failh raha hai.\n\n"
            "Agar aap chahein toh main aapke liye ek general self-care routine bana sakti hoon, "
            "jo treatment-focused nahi hoga."
        )
    elif lang in ("marathi", "marathi_english_mix"):
        return (
            "Mala rash kinva skin reaction che karan sangta yenaar nahi, aani cosmetic product "
            "treatment mhanun suggest karta yenaar nahi.\n\n"
            "Skin reactions che vegvegle karan asu shaktat, mhanun doctor kinva dermatologist "
            "shi bolane best aahe — especially jar te vadhat aahe, dukhat aahe, kinva pasat aahe.\n\n"
            "Tumhala pahije tar mi tumchya sathi ek general self-care routine banu shakte, "
            "jo treatment-focused nasel."
        )
    else:
        return (
            "I can't tell what's causing a rash, and I don't want to suggest a product "
            "that could make it worse.\n\n"
            "Skin reactions can have different causes, so it's best to speak with a "
            "doctor or dermatologist — especially if it's getting worse, painful, or spreading.\n\n"
            "If you'd like, I can still help you build a general self-care routine "
            "that isn't treatment-focused."
        )

def validate_response(response: str) -> SafetyCheckResult:
    """
    Checks the generated response to ensure the LLM didn't invent products
    or make wild medical claims.
    """
    response_lower = response.lower()
    
    medical_claims = ["cure", "heal", "treats", "medicine", "prescription",
                      "ilaaj", "dawai", "upchar"]
    if any(claim in response_lower for claim in medical_claims):
        return SafetyCheckResult(
            status="UNSAFE",
            message="Response contained prohibited medical claims."
        )
        
    return SafetyCheckResult(status="SAFE", message="Response is safe.")
