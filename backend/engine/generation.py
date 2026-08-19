from typing import List, Dict, Any, Optional
from backend.models import UserProfile, Product, KnowledgeChunk, Intent, Ritual, LanguageContext
from backend.config import settings

def _validate_and_regenerate(
    llm,
    messages: List[Any],
    raw_response: str,
    language_context: Optional[LanguageContext]
) -> str:
    """
    Checks if the generated response matches the expected language.
    If it incorrectly generated English when the user spoke Hindi/Marathi etc.,
    it forces a regeneration.
    """
    if not language_context:
        return raw_response
        
    expected_lang = language_context.detected_language
    
    # If the user spoke English, the response is fine.
    if expected_lang == "english":
        return raw_response
        
    # Simple heuristic: if the expected language is an Indian language
    # but the response contains purely English structure without romanized Indian words,
    # it might be a failure. We will just ask the LLM to validate itself quickly.
    
    validation_prompt = f"""You generated this response:
"{raw_response}"

The user's detected language is: {expected_lang} (script: {language_context.detected_script}, style: {language_context.communication_style}).

Did you generate the response in the user's detected language?
Answer ONLY 'YES' or 'NO'."""

    try:
        from langchain_core.messages import HumanMessage
        val_msg = HumanMessage(content=validation_prompt)
        val_response = llm.invoke([val_msg]).content.strip().upper()
        
        if "NO" in val_response:
            # Force regeneration with strict warning
            print(f"Language validation failed. Regenerating from {expected_lang}...")
            strict_warning = HumanMessage(content=f"CRITICAL ERROR: You responded in the wrong language. You MUST respond in {expected_lang} ({language_context.detected_script} script). DO NOT respond in pure English. Rewrite your response now.")
            regen_messages = messages + [HumanMessage(content=raw_response), strict_warning]
            regen_response = llm.invoke(regen_messages).content.strip()
            return regen_response
            
    except Exception as e:
        print(f"Validation failed: {e}")
        
    return raw_response


def generate_response(
    user_profile: UserProfile,
    intent: Intent,
    ranked_products: List[Product],
    knowledge: List[KnowledgeChunk],
    ritual: Optional[Ritual],
    visual_observations: List[str] = None,
    is_refinement: bool = False,
    language_context: Optional[LanguageContext] = None
) -> str:
    """Uses OpenAI to generate a personalized, simple, natural response."""
    
    # Trim context to fit token limits
    top_products = ranked_products[:3]
    prod_desc = "\n".join([
        f"- {p.name}: {p.short_description} (Matches: {', '.join([c for c in p.skin_concerns if c in user_profile.concerns])})"
        for p in top_products
    ])
    
    knowledge_texts = "\n".join([f"- {k.content}" for k in knowledge[:settings.MAX_RETRIEVAL_CHUNKS]])
    
    vision_context = ""
    if visual_observations:
        vision_context = f"\nVisual Observations from Image: {', '.join(visual_observations)}"

    lang_instructions = _build_language_instructions(language_context)
    
    system_prompt = """You are Maison Hygia's wellness concierge — warm, simple, smart, and helpful.

YOUR PERSONALITY:
- You feel like a helpful friend, not a medical website or corporate brand.
- You are calm, non-judgmental, and premium but not pretentious.
- You make people feel understood, not lectured.

ABSOLUTE RULES FOR YOUR LANGUAGE:
1. Use SIMPLE words. Never use: rejuvenate, alleviate, therapeutic, comprehensive, formulation, physiological, environmental stressors, dermatological, antioxidant properties, synergistic, optimal, facilitate, mitigate, inflammatory response, curated, aforementioned, incorporating.
2. Prefer: refresh, help, simple, useful, good for, supports, gentle, easy, daily, comfortable, works well.
3. Keep sentences SHORT. Maximum 15-20 words per sentence.
4. Use conversational openers: "Got it.", "Sure.", "That makes sense.", "Let's keep it simple."
5. NEVER start with "Thank you for sharing" or "I understand your requirements" or "Based on your stated preferences".
6. NEVER sound like a translated document. Write naturally.
7. Structure recommendations with numbered steps, not long paragraphs.
8. Explain WHY a product was chosen conversationally. E.g., "You mentioned dryness, so I picked this because hydration is its main focus." Do NOT use checkmarks (✓).
9. Keep total response under 120 words for simple answers, under 200 words for recommendations.
10. Do NOT make medical claims. Use "helps", "supports", "good for" instead of "treats", "cures", "heals".
11. Keep official product names unchanged (e.g., Deep Hydration Botanical Cream).
12. Do NOT repeatedly say "You said..." or "Based on your preferences...". State things naturally."""

    user_prompt = f"""{lang_instructions}

User's Needs:
- Concerns: {', '.join(user_profile.concerns) if user_profile.concerns else 'Not specified yet'}
- Preferred time: {user_profile.preferred_routine_time or 'Any'}
- Complexity: {user_profile.complexity_tolerance or 'Not specified'}
- Max products requested: {user_profile.max_products or 'No limit stated'}
{vision_context}

Product Knowledge:
{knowledge_texts if knowledge_texts.strip() else 'No specific knowledge retrieved.'}

Recommended Products (DO NOT translate product names):
{prod_desc}

Now write a recommendation response. Follow the language and tone rules exactly."""

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        
        llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=settings.MAX_OUTPUT_TOKENS, temperature=0)
            
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response_text = llm.invoke(messages).content.strip()
        
        # Validation Loop
        response_text = _validate_and_regenerate(llm, messages, response_text, language_context)
        
        return response_text
        
    except Exception as e:
        print(f"LLM Generation failed: {e}")
        if ritual and ritual.steps:
            return _fallback_response(ritual, user_profile)
        prod_names = [p.name for p in top_products]
        return f"Based on what you've told me, I'd suggest starting with {prod_names[0] if prod_names else 'our hydration products'}."


def generate_question_response(
    question_text: str,
    language_context: Optional[LanguageContext]
) -> str:
    """Adapts a follow-up question to the user's detected language and style."""
    
    lang_instructions = _build_language_instructions(language_context)
    
    system_prompt = """You are Maison Hygia's wellness concierge. You need to ask the user a follow-up question.
    
    RULES:
    1. Keep it brief and friendly.
    2. Ask the question naturally.
    3. Output ONLY the translated/adapted question text. Do not add conversational filler like "Sure, I can help."
    4. Keep the question very simple."""

    user_prompt = f"""{lang_instructions}

The question you need to ask is: "{question_text}"

Translate and adapt this question into the requested language and style."""

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        
        llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=100, temperature=0)
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        
        response_text = llm.invoke(messages).content.strip()
        response_text = _validate_and_regenerate(llm, messages, response_text, language_context)
        
        # Strip any quotes the LLM might have added
        if response_text.startswith('"') and response_text.endswith('"'):
            response_text = response_text[1:-1]
            
        return response_text
    except Exception as e:
        print(f"LLM Question Generation failed: {e}")
        return question_text


def generate_safety_response(language_context: Optional[LanguageContext]) -> str:
    """Generates a medical safety refusal in the user's detected language."""
    
    lang_instructions = _build_language_instructions(language_context)
    
    system_prompt = """You are Maison Hygia's wellness concierge. The user has described a medical condition (e.g., rash, pain, infection).
    You must refuse to provide a product for treatment, suggest they see a doctor, but offer a general self-care routine instead.
    
    RULES:
    1. Be empathetic but firm about not treating medical conditions.
    2. Do NOT act like a doctor.
    3. Output ONLY the refusal message."""

    user_prompt = f"""{lang_instructions}

Write a safety refusal message covering these points:
- I cannot diagnose what is causing this skin reaction/rash/pain.
- I will not suggest a cosmetic product as a treatment.
- Please consult a doctor or dermatologist, especially if it gets worse.
- If you want, I can still help you build a general self-care routine that is not treatment-focused.

Write this naturally in the requested language and style."""

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        
        llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=250, temperature=0)
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        
        response_text = llm.invoke(messages).content.strip()
        response_text = _validate_and_regenerate(llm, messages, response_text, language_context)
        
        return response_text
    except Exception as e:
        print(f"LLM Safety Generation failed: {e}")
        return "I can't tell what's causing a rash, and I don't want to suggest a product that could make it worse. Skin reactions can have different causes, so it's best to speak with a doctor or dermatologist. If you'd like, I can still help you build a general self-care routine that isn't treatment-focused."


def _build_language_instructions(language_context: Optional[LanguageContext]) -> str:
    """Builds specific instructions for the LLM about how to respond
    based on the user's detected language and communication style."""
    
    if not language_context:
        return "Respond in simple, conversational English."
    
    lang = language_context.detected_language
    style = language_context.communication_style
    script = language_context.detected_script
    
    # CRITICAL: If language is english, strictly enforce english
    if lang == "english":
        return f"CRITICAL: The user is speaking purely in English. You MUST respond in simple, {'casual and friendly' if style == 'casual' else 'warm and clear'} English. DO NOT use Hindi or Hinglish words."
    
    # Enforce script
    script_instruction = "romanized script (Latin letters)"
    if script == "devanagari" or script == "hindi":
        script_instruction = "Devanagari script (हिंदी)"
    elif script == "marathi":
        script_instruction = "Devanagari script (मराठी)"
        
    if lang == "hindi":
        return (
            f"CRITICAL: You MUST respond in natural, conversational Hindi using {script_instruction}. "
            "Do NOT use formal/textbook Hindi. Write like a friendly person would naturally speak. "
            "Example good tone (Roman): 'Aapki skin dry feel ho rahi hai, toh hum ek simple routine bana sakte hain.' "
            "Example good tone (Devanagari): 'बिल्कुल। अगर आपकी स्किन ड्राई लग रही है, तो हम एक simple routine रख सकते हैं।' "
            "Do NOT output pure English."
        )
    
    elif lang == "hinglish":
        return (
            "CRITICAL: You MUST respond in natural Hinglish — mix Hindi and English the way young Indians naturally speak. "
            "Use romanized Hindi (Latin letters), not Devanagari. "
            "Example: 'Sure! Dry skin ke liye hum bas 2 simple steps se start kar sakte hain.' "
            "Mix naturally. Do NOT force everything into one language. Do NOT output pure English."
        )
    
    elif lang in ("marathi", "marathi_english_mix"):
        return (
            f"CRITICAL: You MUST respond in natural, conversational Marathi using {script_instruction}. "
            "Mix with English where natural. Write like a friendly Marathi-speaking person would. "
            "Example: 'Tumchi skin dry aahe, tar ek simple routine banu ya — zyada products nahi lagtil.' "
            "Do NOT output pure English."
        )
    
    elif "mix" in lang or language_context.is_code_switched:
        base_lang = lang.split("_")[0] if "_" in lang else lang
        return (
            f"CRITICAL: You MUST respond in a natural mix of {base_lang} and English (code-switching), "
            f"using {script_instruction}. Match the user's natural mixing style. "
            f"Keep it {'casual and friendly' if style == 'casual' else 'warm and helpful'}. "
            "Do NOT output pure English."
        )
    
    else:
        # Fallback for other languages
        return (
            f"The user communicated in {lang}. Respond in simple, warm English, but if you can naturally include a few words in romanized {lang}, do so. "
            f"Prioritize clarity and simplicity."
        )


def _fallback_response(ritual: Ritual, user_profile: UserProfile) -> str:
    """Simple template fallback when LLM fails."""
    steps_text = []
    for step in ritual.steps:
        steps_text.append(f"**{step.step_number}. {step.product.name}**\n{step.product.short_description}")
    
    routine_time = user_profile.preferred_routine_time or "daily"
    header = f"Here's a simple {routine_time} routine for you:\n\n"
    
    return header + "\n\n".join(steps_text)
