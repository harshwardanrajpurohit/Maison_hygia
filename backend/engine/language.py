"""
Language Intelligence Layer for Maison Hygia.

Handles:
- Language detection (Hindi, Hinglish, Marathi, English, mixed, romanized regional)
- Communication style detection (casual vs formal)
- Normalization to English for downstream pipeline
- Code-switching detection
- Cultural context signal extraction (Ayurveda, climate, home remedies, etc.)
- Spelling variation tolerance (acha/accha/achha)
"""

import json
from typing import Dict, Any, List, Optional
from backend.models import LanguageContext
from backend.config import settings


def analyze_and_normalize(
    raw_message: str,
    conversation_history: List[Dict[str, Any]] = None,
    previous_language_context: Optional[LanguageContext] = None
) -> LanguageContext:
    """
    Analyzes a user message to detect language, style, and cultural signals,
    then normalizes the message to English for downstream processing.
    
    Uses a single OpenAI LLM call for efficiency.
    """
    if not raw_message or not raw_message.strip():
        return LanguageContext(normalized_message=raw_message or "")

    # Build context from previous turns for continuity
    history_context = ""
    if conversation_history and len(conversation_history) > 0:
        recent = conversation_history[-4:]  # Last 2 exchanges
        history_lines = []
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content:
                history_lines.append(f"{role}: {content[:150]}")
        if history_lines:
            history_context = "\n".join(history_lines)

    prev_lang = "unknown"
    if previous_language_context:
        prev_lang = previous_language_context.detected_language

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=400)

        prompt = f"""Analyze this user message from an Indian wellness app. The user may write in English, Hindi, Hinglish, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Punjabi, or any mix of these — often in romanized/transliterated form (Latin script).

Output ONLY a JSON object with these fields:
- "normalized_english": string — A clean, natural English translation/interpretation of the user's message. Preserve the EXACT meaning and all details. If already English, keep it as-is.
- "detected_language": string — One of: "english", "hindi", "hinglish", "marathi", "tamil", "telugu", "bengali", "gujarati", "kannada", "malayalam", "punjabi", or "<language>_english_mix" for mixed (e.g. "marathi_english_mix").
- "detected_script": string — "latin", "devanagari", "tamil_script", "mixed", etc.
- "is_code_switched": boolean — true if the user mixed two or more languages in a single message
- "communication_style": string — "casual" or "formal" based on the tone (slang like "yaar", abbreviations = casual)
- "cultural_signals": array of strings — Any of: "ayurveda", "natural_ingredients", "home_remedy", "climate_concern", "seasonal", "festival", "family_recommendation", "traditional_routine", "pollution", "lifestyle_stress". Only include if actually present in the message.
- "product_count_preference": integer or null — If the user explicitly states how many products they want (e.g. "bas 2 products"), extract the number. Otherwise null.

CRITICAL RULES FOR LANGUAGE DETECTION:
- If the text is purely English with NO Hindi/Indian words (e.g., "I want a simple evening routine for dry skin"), you MUST classify it as "english", NOT "hinglish". The Indian context of the app does not make English text Hinglish.
- "hinglish" should ONLY be used when Hindi words are mixed with English words, or when Hindi is written in Latin script (e.g., "Meri skin dry hai").

Handle these challenges:
- Romanized Hindi: "meri skin dry hai" = "My skin is dry"
- Romanized Marathi: "mala simple routine pahije" = "I need a simple routine"
- Spelling variations: "acha"/"accha"/"achha" all mean "good/okay"
- Slang: "yaar" = casual address, not meaningful content
- Incomplete sentences: "skin dry kya kru" = "My skin is dry, what should I do?"
- Mixed languages: "Meri skin dry hai but mujhe heavy products nahi chahiye" = "My skin is dry but I don't want heavy products"
- Ambiguous/Short inputs: If the user just says "haan", "yes", "2", "night", default to the `Previous language in conversation` if it's available. Do not reset to English just because the word "night" or "2" was used.

Previous language in conversation: {prev_lang}

Recent conversation context:
{history_context if history_context else "No previous context."}

User message to analyze:
\"{raw_message}\""""

        response = llm.invoke([
            SystemMessage(content="You are a multilingual language analysis system for an Indian wellness app. Output ONLY valid JSON, no markdown."),
            HumanMessage(content=prompt)
        ])

        content = response.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)

        return LanguageContext(
            detected_language=data.get("detected_language", "english"),
            detected_script=data.get("detected_script", "latin"),
            is_code_switched=data.get("is_code_switched", False),
            communication_style=data.get("communication_style", "casual"),
            response_language_preference="auto",
            cultural_signals=data.get("cultural_signals", []),
            normalized_message=data.get("normalized_english", raw_message)
        )

    except Exception as e:
        print(f"Language analysis failed: {e}. Using raw message as fallback.")
        # Fallback: use raw message with basic detection
        return _fallback_analysis(raw_message)


def _fallback_analysis(raw_message: str) -> LanguageContext:
    """
    Basic keyword-based fallback when the LLM call fails.
    Detects common Hindi/Hinglish patterns and does minimal normalization.
    """
    msg_lower = raw_message.lower().strip()

    # Basic Hindi/Hinglish detection
    hindi_markers = [
        "meri", "mujhe", "chahiye", "hai", "hain", "kya", "karo", "batao",
        "nahi", "bohot", "bahut", "acha", "accha", "thoda", "zyada",
        "yaar", "haan", "naa", "kuch", "kaise", "kab", "kaun",
        "raat", "subah", "shaam", "din", "skin", "lagau", "lagana",
        "pasand", "bilkul", "bas", "sirf", "simple", "routine"
    ]
    marathi_markers = [
        "mala", "pahije", "aahe", "zali", "khup", "changla", "sathi",
        "karun", "dya", "nako", "mhanun", "tar", "ata"
    ]

    words = set(msg_lower.split())

    hindi_count = len(words.intersection(hindi_markers))
    marathi_count = len(words.intersection(marathi_markers))
    has_english = any(w in msg_lower for w in ["want", "need", "please", "help", "my", "the", "for"])

    detected_language = "english"
    is_code_switched = False

    if marathi_count >= 2:
        detected_language = "marathi" if not has_english else "marathi_english_mix"
        is_code_switched = has_english
    elif hindi_count >= 2:
        if has_english:
            detected_language = "hinglish"
            is_code_switched = True
        else:
            detected_language = "hindi"
    elif hindi_count >= 1 and has_english:
        detected_language = "hinglish"
        is_code_switched = True

    # Detect casual style
    casual_markers = ["yaar", "bhai", "bro", "lol", "haha", "na", "re"]
    style = "casual" if any(m in words for m in casual_markers) else "casual"

    return LanguageContext(
        detected_language=detected_language,
        detected_script="latin",
        is_code_switched=is_code_switched,
        communication_style=style,
        response_language_preference="auto",
        cultural_signals=[],
        normalized_message=raw_message  # Can't normalize without LLM
    )
