import base64
import os
from typing import Dict, Any, Optional
from backend.config import settings

def process_image(image_bytes: bytes, image_type: str) -> Dict[str, Any]:
    """
    Validates and processes an image, extracting structured visual features.
    Uses OpenAI GPT-4o for vision analysis.
    """
    # 1. Validation
    # Limit size to 5MB
    if len(image_bytes) > 5 * 1024 * 1024:
        raise ValueError("Image file too large. Maximum size is 5MB.")
    
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if image_type not in allowed_types:
        raise ValueError(f"Unsupported image type: {image_type}. Allowed types: {', '.join(allowed_types)}")

    # 2. Extract visual information
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        # Use gpt-4o for vision
        llm = ChatOpenAI(model="gpt-4o", max_tokens=settings.MAX_OUTPUT_TOKENS)
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this face/skin image and identify any visible skin concerns (e.g. acne, redness, dryness, dullness). Output a concise comma-separated list of concerns."},
                {"type": "image_url", "image_url": {"url": f"data:{image_type};base64,{base64_image}"}}
            ]
        )
        response = llm.invoke([message])
        analysis = response.content
            
        # Parse the comma-separated list
        detected_concerns = [c.strip().lower() for c in analysis.split(',') if c.strip()]
        
        return {
            "status": "success",
            "detected_concerns": detected_concerns,
            "raw_analysis": analysis
        }
        
    except Exception as e:
        print(f"Vision analysis failed: {e}")
        return {
            "status": "failed",
            "detected_concerns": [],
            "raw_analysis": "Vision analysis unavailable."
        }
