from typing import List
from backend.models import Product

MOCK_PRODUCTS = [
    Product(
        id="p01",
        name="Sandalwood Melt Cleansing Balm",
        category="Botanical Beauty",
        description="A gentle first step for removing makeup and impurities. Infused with soothing sandalwood to begin an evening wind-down ritual.",
        short_description="Gentle evening makeup remover.",
        ingredients=["Sandalwood Oil", "Sweet Almond Oil", "Mango Butter"],
        intended_benefit="Cleanse without stripping moisture.",
        routine_time="evening",
        skin_concerns=["dry", "sensitive"],
        wellness_goals=["evening_relaxation", "cleanse"],
        routine_stage="cleanse",
        price=32.0,
        margin="medium",
        evidence_quality=0.85,
        tags=["calming", "simple", "balm"]
    ),
    Product(
        id="p02",
        name="Amla Vitamin C Boost",
        category="Botanical Beauty",
        description="A powerful antioxidant serum to brighten and protect the skin throughout the day.",
        short_description="Morning brightening serum.",
        ingredients=["Amla Extract", "Vitamin C", "Hyaluronic Acid"],
        intended_benefit="Brighten dull skin and provide antioxidant protection.",
        routine_time="morning",
        skin_concerns=["dull", "aging"],
        wellness_goals=["skin_glow", "protection"],
        routine_stage="treat",
        price=48.0,
        margin="high",
        evidence_quality=0.92,
        tags=["brightening", "serum"]
    ),
    Product(
        id="p03",
        name="Rose Tinted Lip Balm",
        category="Botanical Beauty",
        description="A deeply nourishing lip treatment with a subtle hint of rose.",
        short_description="Nourishing daily lip care.",
        ingredients=["Rose Absolute", "Shea Butter", "Beeswax"],
        intended_benefit="Hydrate and protect lips.",
        routine_time="any",
        skin_concerns=["dry"],
        wellness_goals=["hydration", "simple_care"],
        routine_stage="treat",
        price=18.0,
        margin="high",
        evidence_quality=0.80,
        tags=["simple", "hydration", "lips"]
    ),
    Product(
        id="p04",
        name="Ashwagandha Calm Overnight Mask",
        category="Botanical Beauty",
        description="A rich, restorative overnight treatment leveraging adaptogenic ashwagandha to repair stressed skin while you sleep.",
        short_description="Restorative overnight mask.",
        ingredients=["Ashwagandha", "Ceramides", "Squalane"],
        intended_benefit="Repair skin barrier and reduce visible stress.",
        routine_time="evening",
        skin_concerns=["dry", "stressed", "aging"],
        wellness_goals=["evening_relaxation", "repair", "skin_hydration"],
        routine_stage="moisturize",
        price=55.0,
        margin="high",
        evidence_quality=0.88,
        tags=["calming", "overnight", "repair"]
    ),
    Product(
        id="p05",
        name="Evening Calm Tea",
        category="Ritual Nutrition",
        description="A caffeine-free herbal blend designed to quiet the mind and prepare the body for restful sleep.",
        short_description="Relaxing evening herbal tea.",
        ingredients=["Chamomile", "Lavender", "Lemon Balm", "Valerian Root"],
        intended_benefit="Promote relaxation and better sleep quality.",
        routine_time="evening",
        skin_concerns=[],
        wellness_goals=["evening_relaxation", "sleep"],
        routine_stage="wind_down",
        price=22.0,
        margin="medium",
        evidence_quality=0.90,
        tags=["calming", "simple", "tea", "internal"]
    ),
    Product(
        id="p06",
        name="Deep Hydration Botanical Cream",
        category="Botanical Beauty",
        description="An intensely moisturizing cream that locks in hydration without feeling heavy.",
        short_description="Intense daily moisturizer.",
        ingredients=["Gotu Kola", "Glycerin", "Jojoba Oil"],
        intended_benefit="Provide deep, lasting hydration.",
        routine_time="any",
        skin_concerns=["dry", "flaky"],
        wellness_goals=["skin_hydration", "protection"],
        routine_stage="moisturize",
        price=42.0,
        margin="high",
        evidence_quality=0.95,
        tags=["hydration", "simple", "cream"]
    ),
    Product(
        id="p07",
        name="Tulsi Clarity Mist",
        category="Botanical Beauty",
        description="A refreshing facial mist to balance and clarify the skin throughout the day.",
        short_description="Refreshing balancing mist.",
        ingredients=["Tulsi (Holy Basil)", "Rose Water", "Aloe Vera"],
        intended_benefit="Balance oil production and refresh the senses.",
        routine_time="any",
        skin_concerns=["oily", "dull"],
        wellness_goals=["refresh", "balance"],
        routine_stage="prepare",
        price=24.0,
        margin="medium",
        evidence_quality=0.75,
        tags=["refreshing", "simple", "mist"]
    )
]

def get_all_products() -> List[Product]:
    return MOCK_PRODUCTS

def get_product_by_id(product_id: str) -> Product:
    for p in MOCK_PRODUCTS:
        if p.id == product_id:
            return p
    return None
