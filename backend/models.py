from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class LanguageContext(BaseModel):
    """Tracks the user's language and communication style across the conversation."""
    detected_language: str = "english"  # english, hindi, hinglish, marathi, tamil, etc.
    detected_script: str = "latin"  # latin, devanagari, mixed
    is_code_switched: bool = False  # True if user mixed languages in one message
    communication_style: str = "casual"  # casual, formal, mixed
    response_language_preference: str = "auto"  # auto = mirror user's language
    cultural_signals: List[str] = []  # e.g. ["ayurveda", "climate_concern", "home_remedy"]
    normalized_message: str = ""  # The English-normalized version of the user's message

class RitualPillar(str, Enum):
    GLOW = "Glow"
    PAUSE = "Pause"
    NOURISH = "Nourish"
    CARE = "Care"
    GATHER = "Gather"

class Product(BaseModel):
    id: str
    name: str
    category: str
    description: str
    short_description: Optional[str] = ""
    ingredients: List[str] = []
    intended_benefit: str = ""
    routine_time: str = "any" # morning, evening, any
    skin_concerns: List[str] = []
    wellness_goals: List[str] = []
    routine_stage: str = "" # cleanse, treat, moisturize, etc.
    price: float = 0.0
    margin: str = "low" # low, medium, high
    evidence_quality: float = 0.5 # 0.0 to 1.0
    caution_notes: Optional[str] = None
    tags: List[str] = []
    availability: bool = True

class Intent(BaseModel):
    primary_goal: Optional[str] = None
    secondary_goal: Optional[str] = None
    concerns: List[str] = []
    preferences: Dict[str, Any] = {} # e.g. {"texture": "gel", "fragrance_level": "low"}
    routine_time: Optional[str] = None # e.g. "evening"
    budget: Optional[str] = None
    complexity: Optional[str] = None # e.g. "simple", "comprehensive"
    category_preference: Optional[str] = None
    medical_risk: bool = False
    missing_information: List[str] = []
    confidence_scores: Dict[str, float] = {}
    language: Optional[str] = None
    request_type: str = "recommendation" # greeting, clarification, recommendation, product_information

class UserProfile(BaseModel):
    user_id: str = "default_user"
    concerns: List[str] = []
    primary_goal: Optional[str] = None
    secondary_goal: Optional[str] = None
    ritual_moment: Optional[RitualPillar] = None
    preferred_routine_time: Optional[str] = None
    budget: Optional[str] = None
    complexity_tolerance: Optional[str] = None
    sensory_preferences: Dict[str, str] = {}
    liked_products: List[str] = []
    disliked_products: List[str] = []
    disliked_attributes: List[str] = []
    language: str = "english"
    communication_style: str = "casual"  # casual, formal
    max_products: Optional[int] = None  # User-stated product count limit

class KnowledgeChunk(BaseModel):
    id: str
    content: str
    source_url: str = ""
    source_type: str = ""
    trust_level: str = ""
    tags: List[str] = []
    category: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Question(BaseModel):
    id: str
    text: str
    options: List[str] = []
    dimension: str # what profile field it maps to
    information_gain_score: float = 0.0

class ScoreBreakdown(BaseModel):
    total_score: float
    factors: Dict[str, float]

class RitualStep(BaseModel):
    step_number: int
    stage_name: str
    product: Product
    why_selected: str = ""

class Ritual(BaseModel):
    moment: str
    steps: List[RitualStep]
    total_price: float
    why_this_ritual: List[str] = []

class ConversationState(BaseModel):
    id: str
    user_profile: UserProfile = Field(default_factory=UserProfile)
    history: List[Dict[str, Any]] = []
    intent: Optional[Intent] = None
    current_ritual: Optional[Ritual] = None
    state: str = "GREETING" # GREETING, DISCOVERY, CLARIFICATION, RECOMMENDATION, RITUAL_BUILDING, REFINEMENT, SAFETY, FEEDBACK, PRODUCT_INFORMATION
    safety_status: str = "SAFE" # SAFE, MEDICAL_RISK
    developer_data: Dict[str, Any] = {} # For the debug panel
    language_context: LanguageContext = Field(default_factory=LanguageContext)
