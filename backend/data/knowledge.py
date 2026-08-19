from typing import List
from backend.models import KnowledgeChunk

# 25+ Knowledge base entries covering Ayurveda, rituals, ingredients
KNOWLEDGE_BASE = [
    KnowledgeChunk(
        id="k1",
        content="Turmeric (Haridra) is highly revered in Ayurveda for its potent anti-inflammatory and antioxidant properties. When applied topically, it helps even out skin tone and brings out a natural radiance.",
        source_url="https://maisonhygia.com/learn/turmeric",
        source_type="internal_expert",
        trust_level="high",
        tags=["turmeric", "ingredient", "glow", "anti-inflammatory"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k2",
        content="Saffron (Kumkuma) is considered a precious ingredient that promotes a luminous complexion. It is rich in vitamins and antioxidants, making it excellent for brightening dull or aging skin.",
        source_url="https://maisonhygia.com/learn/saffron",
        source_type="internal_expert",
        trust_level="high",
        tags=["saffron", "ingredient", "brightening", "glow"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k3",
        content="Ashwagandha is a powerful adaptogen that helps the body and skin cope with stress. In skincare, it reduces the visible signs of fatigue and promotes a calmer, more resilient skin barrier.",
        source_url="https://maisonhygia.com/learn/ashwagandha",
        source_type="clinical_summary",
        trust_level="high",
        tags=["ashwagandha", "ingredient", "stress", "adaptogen"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k4",
        content="Makhana, or fox nuts, are a highly nutritious aquatic seed. They are low in calories, high in protein and antioxidants, and traditionally used to provide sustained energy without a heavy feeling.",
        source_url="https://maisonhygia.com/learn/makhana",
        source_type="internal_expert",
        trust_level="high",
        tags=["makhana", "ingredient", "nutrition", "snack"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k5",
        content="Ayurveda emphasizes the concept of Dinacharya, or daily routines. Establishing a consistent morning and evening ritual aligns the body with natural circadian rhythms, improving both skin health and mental clarity.",
        source_url="https://maisonhygia.com/learn/dinacharya",
        source_type="tradition",
        trust_level="medium",
        tags=["dinacharya", "routine", "ayurveda", "lifestyle"],
        category="Ayurvedic Concepts"
    ),
    KnowledgeChunk(
        id="k6",
        content="A proper morning 'Glow' ritual typically involves gentle cleansing, targeted treatment (like a vitamin C or saffron serum), and lightweight hydration to protect the skin throughout the day.",
        source_url="https://maisonhygia.com/learn/glow-ritual",
        source_type="internal_expert",
        trust_level="high",
        tags=["glow", "morning", "routine", "skincare"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k7",
        content="The evening 'Pause' ritual is crucial for skin repair and mental wind-down. It focuses on removing impurities with richer cleansers or balms, followed by deeply nourishing moisturizers or adaptogenic treatments.",
        source_url="https://maisonhygia.com/learn/pause-ritual",
        source_type="internal_expert",
        trust_level="high",
        tags=["pause", "evening", "routine", "skincare", "sleep"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k8",
        content="In Ayurveda, dry skin is often associated with a Vata imbalance. It benefits from rich, warming, and deeply nourishing textures like heavy creams, oils, and ingredients like sesame and ghee.",
        source_url="https://maisonhygia.com/learn/doshas-vata",
        source_type="tradition",
        trust_level="medium",
        tags=["vata", "dry", "ayurveda", "skincare"],
        category="Ayurvedic Concepts"
    ),
    KnowledgeChunk(
        id="k9",
        content="Oily or acne-prone skin is linked to excess Kapha or Pitta. It requires clarifying, purifying, and cooling ingredients such as neem, tulsi, and vetiver, in lightweight gel or water textures.",
        source_url="https://maisonhygia.com/learn/doshas-kapha",
        source_type="tradition",
        trust_level="medium",
        tags=["kapha", "pitta", "oily", "acne", "ayurveda"],
        category="Ayurvedic Concepts"
    ),
    KnowledgeChunk(
        id="k10",
        content="Neem is a highly revered botanical known for its antibacterial and purifying properties. It is exceptionally effective at managing breakouts and maintaining a clear, balanced complexion.",
        source_url="https://maisonhygia.com/learn/neem",
        source_type="clinical_summary",
        trust_level="high",
        tags=["neem", "ingredient", "acne", "purifying"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k11",
        content="Tulsi, or Holy Basil, is considered a sacred plant in India. Topically, it acts as an antimicrobial and antioxidant agent, purifying the skin and invigorating the senses.",
        source_url="https://maisonhygia.com/learn/tulsi",
        source_type="internal_expert",
        trust_level="high",
        tags=["tulsi", "ingredient", "purifying", "antioxidant"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k12",
        content="Abhyanga is the Ayurvedic practice of self-massage with warm oil. This deeply restorative practice not only nourishes the skin but also calms the nervous system and improves circulation.",
        source_url="https://maisonhygia.com/learn/abhyanga",
        source_type="tradition",
        trust_level="medium",
        tags=["abhyanga", "massage", "body", "care"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k13",
        content="Vetiver (Ushira) is a grounding, cooling root that provides excellent lightweight hydration and helps refine pores. Its earthy scent is also known to promote a sense of calm.",
        source_url="https://maisonhygia.com/learn/vetiver",
        source_type="internal_expert",
        trust_level="high",
        tags=["vetiver", "ingredient", "cooling", "oily"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k14",
        content="Sandalwood (Chandana) is prized for its soothing, anti-inflammatory properties. It is incredibly gentle on sensitive skin and its fragrance is deeply relaxing, making it ideal for evening rituals.",
        source_url="https://maisonhygia.com/learn/sandalwood",
        source_type="internal_expert",
        trust_level="high",
        tags=["sandalwood", "ingredient", "soothing", "evening"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k15",
        content="A 'Nourish' moment integrates functional nutrition into the day. Snacks containing nuts, seeds, and adaptogens provide sustained energy without spiking blood sugar, supporting overall wellness from the inside out.",
        source_url="https://maisonhygia.com/learn/nourish-moment",
        source_type="internal_expert",
        trust_level="high",
        tags=["nourish", "snack", "nutrition", "wellness"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k16",
        content="The 'Gather' pillar celebrates community and shared experiences. Traditional foods like spiced nuts and dates are perfect for sharing, fostering connection while providing nutritional benefits.",
        source_url="https://maisonhygia.com/learn/gather-pillar",
        source_type="tradition",
        trust_level="medium",
        tags=["gather", "community", "sharing", "snack"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k17",
        content="Amla (Indian Gooseberry) is one of the most potent natural sources of Vitamin C. It offers powerful antioxidant protection, brightens the skin, and strengthens hair follicles when used in scalp treatments.",
        source_url="https://maisonhygia.com/learn/amla",
        source_type="clinical_summary",
        trust_level="high",
        tags=["amla", "ingredient", "vitamin-c", "hair", "brightening"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k18",
        content="Brahmi (Gotu Kola) stimulates collagen production and improves circulation. It is highly effective in firming treatments, especially around the delicate eye area.",
        source_url="https://maisonhygia.com/learn/brahmi",
        source_type="clinical_summary",
        trust_level="high",
        tags=["brahmi", "gotu-kola", "ingredient", "firming", "anti-aging"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k19",
        content="Manjistha is a renowned blood purifier in Ayurveda. In skincare, it helps clear blemishes, reduce hyperpigmentation, and promote a clear, even complexion.",
        source_url="https://maisonhygia.com/learn/manjistha",
        source_type="tradition",
        trust_level="medium",
        tags=["manjistha", "ingredient", "blemish", "clear-skin"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k20",
        content="Bhringraj is famously known as the 'ruler of hair' in Ayurveda. It deeply nourishes the scalp, promotes hair growth, and helps prevent premature graying when massaged regularly.",
        source_url="https://maisonhygia.com/learn/bhringraj",
        source_type="tradition",
        trust_level="high",
        tags=["bhringraj", "ingredient", "hair", "scalp"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k21",
        content="Ritucharya refers to seasonal regimens in Ayurveda. Adapting skincare and nutrition as the seasons change helps maintain balance; for example, using richer products in winter (Vata season).",
        source_url="https://maisonhygia.com/learn/ritucharya",
        source_type="tradition",
        trust_level="medium",
        tags=["ritucharya", "season", "ayurveda", "lifestyle"],
        category="Ayurvedic Concepts"
    ),
    KnowledgeChunk(
        id="k22",
        content="Ghee is clarified butter that is deeply revered in Ayurvedic medicine for its healing and moisturizing properties. It provides intense hydration for very dry skin or chapped lips.",
        source_url="https://maisonhygia.com/learn/ghee",
        source_type="tradition",
        trust_level="medium",
        tags=["ghee", "ingredient", "moisturizing", "dry"],
        category="Ingredient Science"
    ),
    KnowledgeChunk(
        id="k23",
        content="Combining topical skincare with ingestible nutrition creates a holistic ritual. For instance, a glowing complexion is best achieved by combining a brightening serum with antioxidant-rich foods.",
        source_url="https://maisonhygia.com/learn/holistic-beauty",
        source_type="internal_expert",
        trust_level="high",
        tags=["holistic", "beauty", "nutrition", "ritual"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k24",
        content="A minimalist routine (2 steps) focuses on multi-functional products, typically a cleanser and a rich moisturizer. A comprehensive routine (4+ steps) allows for targeted treatments like serums, essences, and masks.",
        source_url="https://maisonhygia.com/learn/routine-complexity",
        source_type="internal_expert",
        trust_level="high",
        tags=["routine", "complexity", "skincare", "minimalist"],
        category="Ritual Design"
    ),
    KnowledgeChunk(
        id="k25",
        content="Stress is a major contributor to skin issues, leading to dullness, breakouts, and premature aging. Incorporating adaptogens like Ashwagandha or Tulsi helps mitigate the physical impact of stress.",
        source_url="https://maisonhygia.com/learn/stress-skin",
        source_type="clinical_summary",
        trust_level="high",
        tags=["stress", "skin", "adaptogen", "wellness"],
        category="Ayurvedic Concepts"
    ),
    KnowledgeChunk(
        id="k26",
        content="Triphala is a traditional herbal formulation of three fruits. While primarily used for digestive health, its detoxifying effects reflect positively on the skin, promoting clarity.",
        source_url="https://maisonhygia.com/learn/triphala",
        source_type="tradition",
        trust_level="medium",
        tags=["triphala", "ingredient", "digestion", "detox"],
        category="Ingredient Science"
    )
]

def get_all_knowledge() -> List[KnowledgeChunk]:
    return KNOWLEDGE_BASE
