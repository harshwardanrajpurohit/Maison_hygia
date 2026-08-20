from typing import Dict, Any, Optional
from backend.models import ConversationState, UserProfile, RitualPillar, LanguageContext
from backend.engine.intent import extract_intent
from backend.engine.questions import select_questions
from backend.engine.recommender import build_ritual
from backend.engine.safety import get_medical_risk_response
from backend.engine.language import analyze_and_normalize
from backend.data.products import get_all_products
from backend.engine.vision import process_image
from backend.engine.retrieval import retrieve_knowledge
from backend.config import settings

class ConversationManager:
    def __init__(self):
        self.states: Dict[str, ConversationState] = {}
        
    def start_conversation(self, conv_id: str) -> Dict[str, Any]:
        state = ConversationState(id=conv_id, state="GREETING")
        self.states[conv_id] = state
        return {
            "conversation_id": conv_id,
            "greeting": (
                "Hi! What would you like help with today? / Aaj aap kis cheez mein help chahte hain?"
            ),
            "initial_questions": []
        }
        
    def handle_feedback(self, state: ConversationState, message: str) -> bool:
        """Handles explicit feedback buttons. Returns True if handled.
        Enhanced with Hinglish/Hindi feedback patterns."""
        msg_lower = message.lower()
        handled = False
        
        # English feedback
        if "simpler" in msg_lower or "fewer steps" in msg_lower:
            state.user_profile.complexity_tolerance = "simple"
            state.user_profile.disliked_attributes.append("complex")
            handled = True
        elif "more hydration" in msg_lower:
            state.user_profile.primary_goal = "skin_hydration"
            if "dry" not in state.user_profile.concerns:
                state.user_profile.concerns.append("dry")
            handled = True
        elif "more relaxation" in msg_lower:
            state.user_profile.secondary_goal = "evening_relaxation"
            if "stressed" not in state.user_profile.concerns:
                state.user_profile.concerns.append("stressed")
            handled = True
        
        # Hinglish/Hindi feedback
        elif "simple" in msg_lower and ("karo" in msg_lower or "rakho" in msg_lower or "chahiye" in msg_lower):
            state.user_profile.complexity_tolerance = "simple"
            state.user_profile.disliked_attributes.append("complex")
            handled = True
            
        return handled

    def process_message(self, conv_id: str, message: str, image_bytes: Optional[bytes] = None, image_type: Optional[str] = None) -> Dict[str, Any]:
        if conv_id not in self.states:
            self.start_conversation(conv_id)
            
        state = self.states[conv_id]
        
        # Memory trimming
        if len(state.history) >= settings.MAX_HISTORY_MESSAGES * 2:
            state.history = [state.history[0]] + state.history[-(settings.MAX_HISTORY_MESSAGES * 2 - 1):]
            
        state.history.append({"role": "user", "content": message, "has_image": bool(image_bytes)})
        
        # Check for explicit feedback button clicks first
        if self.handle_feedback(state, message):
            state.state = "RECOMMENDING"
            return self._generate_recommendation(state, "Got it — I've updated your routine based on your preference.")

        # ── STEP 0: Language Intelligence Layer ─────────────────────
        # Analyze the raw message to detect language, normalize to English,
        # and extract cultural context signals.
        if settings.LANGUAGE_DETECTION_ENABLED:
            language_context = analyze_and_normalize(
                raw_message=message,
                conversation_history=state.history,
                previous_language_context=state.language_context
            )
            state.language_context = language_context
            
            # Update user profile with language preferences
            state.user_profile.language = language_context.detected_language
            state.user_profile.communication_style = language_context.communication_style
            
            # Use normalized English for downstream processing
            normalized_message = language_context.normalized_message
        else:
            normalized_message = message
            language_context = state.language_context

        # ── STEP 1: Vision Pipeline ─────────────────────────────────
        visual_observations = []
        if image_bytes and image_type:
            vision_result = process_image(image_bytes, image_type)
            if vision_result["status"] == "success":
                visual_observations = vision_result["detected_concerns"]
                for vc in visual_observations:
                    if vc not in state.user_profile.concerns:
                        state.user_profile.concerns.append(vc)
                        
        # ── STEP 2: Medical Safety Guardrail (BEFORE Intent extraction) ─
        from backend.engine.safety import should_escalate, get_medical_risk_response
        is_unsafe = should_escalate(message)
        if is_unsafe:
            state.state = "SAFETY"
            state.safety_status = "MEDICAL_RISK"
            response = get_medical_risk_response(language_context)
            state.history.append({"role": "assistant", "content": response})
            return {
                "response": response,
                "visual_observations": visual_observations,
                "safety_status": state.safety_status,
                "developer_data": state.developer_data if hasattr(state, 'developer_data') else {},
                "is_complete": False
            }
            
        state.safety_status = "SAFE"

        # ── STEP 3: Intent Extraction (on normalized English) ───────
        intent_text = normalized_message
        if visual_observations:
            intent_text += f" (Visual concerns detected: {', '.join(visual_observations)})"
            
        intent = extract_intent(intent_text, state.user_profile.model_dump())
        state.intent = intent
        
        # Update user profile from intent
        for c in intent.concerns:
            if c not in state.user_profile.concerns:
                state.user_profile.concerns.append(c)
        if intent.primary_goal: state.user_profile.primary_goal = intent.primary_goal
        if intent.secondary_goal: state.user_profile.secondary_goal = intent.secondary_goal
        if intent.routine_time: state.user_profile.preferred_routine_time = intent.routine_time
        if intent.complexity: state.user_profile.complexity_tolerance = intent.complexity
        if intent.budget: state.user_profile.budget = intent.budget
        
        # Handle product count preference from language analysis
        if intent.preferences.get("max_products"):
            state.user_profile.max_products = intent.preferences["max_products"]
        
        # Populate developer data for the UI
        state.developer_data = {
            "intent": intent.model_dump(),
            "profile": state.user_profile.model_dump(),
            "language": {
                "detected": language_context.detected_language,
                "style": language_context.communication_style,
                "code_switched": language_context.is_code_switched,
                "cultural_signals": language_context.cultural_signals,
                "normalized": language_context.normalized_message[:200]
            }
        }
        
        # If the LLM still detected medical risk, fall back to safety
        if intent.medical_risk:
            state.state = "SAFETY"
            state.safety_status = "MEDICAL_RISK"
            response = get_medical_risk_response(language_context)
            state.history.append({"role": "assistant", "content": response})
            return {
                "response": response,
                "visual_observations": visual_observations,
                "safety_status": state.safety_status,
                "developer_data": state.developer_data,
                "is_complete": False
            }

        # ── STEP 4: Check for Missing Information ───────────────────
        if intent.request_type == "greeting":
            state.state = "GREETING"
            response = "Hello! I'm here to help with your wellness and skincare routine. How can I help you today?"
            if language_context.detected_language in ["hindi", "hinglish"]:
                response = "Namaste! Main aapki skincare aur wellness routine mein madad kar sakti hoon. Aaj main aapki kaise madad karoon?"
            elif language_context.detected_language in ["marathi", "marathi_english_mix"]:
                response = "Namaskar! Mi tumchi skincare aani wellness routine madhe madat karu shakte. Aaj mi tumchi kashi madat karu?"
            state.history.append({"role": "assistant", "content": response})
            return {
                "response": response,
                "visual_observations": visual_observations,
                "safety_status": state.safety_status,
                "developer_data": state.developer_data,
                "is_complete": False
            }

        # ── STEP 4: Three-Question Discovery Framework ───────────────────
        if state.questions_asked_count < 3 and not state.discovery_complete:
            questions = select_questions(intent, state.user_profile, top_n=1)
            if questions:
                state.state = "DISCOVERY"
                q = questions[0]
                from backend.engine.generation import generate_question_response
                adaptive_question = generate_question_response(q.text, language_context)
                
                if language_context and language_context.detected_language == "english":
                    if state.questions_asked_count == 0:
                        response = f"Absolutely. To make sure I suggest the right routine for you, I have a few quick questions.\n\n**{adaptive_question}**"
                    elif state.questions_asked_count == 1:
                        response = f"Got it. That helps me understand your needs better.\n\n**{adaptive_question}**"
                    elif state.questions_asked_count == 2:
                        response = f"Thanks. Just one last question:\n\n**{adaptive_question}**"
                else:
                    response = f"**{adaptive_question}**"
                
                state.history.append({"role": "assistant", "content": response})
                state.questions_asked_count += 1
                
                return {
                    "response": response,
                    "visual_observations": visual_observations,
                    "follow_up_questions": [{"text": adaptive_question, "options": q.options}],
                    "safety_status": state.safety_status,
                    "developer_data": state.developer_data,
                    "is_complete": False
                }
            else:
                state.discovery_complete = True
        else:
            state.discovery_complete = True

        # ── STEP 5: Generate Recommendation ─────────────────────────
        return self._generate_recommendation(state, None, visual_observations)

    def _generate_recommendation(self, state: ConversationState, prefix: str = None, visual_observations: list = None) -> Dict[str, Any]:
        """Internal method to run RAG and build the ritual."""
        if not visual_observations:
            visual_observations = []
            
        # Retrieval (RAG) — uses normalized English for search quality
        search_query = " ".join(state.user_profile.concerns)
        if state.user_profile.primary_goal:
            search_query += f" {state.user_profile.primary_goal}"
            
        retrieved_knowledge = []
        if search_query.strip():
            retrieved_knowledge = retrieve_knowledge(search_query)
            
        # Recommendation Ranking
        all_products = get_all_products()
        ritual = build_ritual(state.user_profile, all_products)
        state.current_ritual = ritual
        
        # Populate developer data with scoring details
        from backend.engine.recommender import score_product
        scores_debug = []
        for p in all_products:
            s, factors = score_product(p, state.user_profile)
            scores_debug.append({"name": p.name, "score": s, "factors": factors})
        scores_debug.sort(key=lambda x: x["score"], reverse=True)
        
        state.developer_data["retrieval"] = [k.content for k in retrieved_knowledge]
        state.developer_data["scores"] = scores_debug[:5]

        # LLM Generation — with language context for adaptive responses
        from backend.engine.generation import generate_response
        raw_response = generate_response(
            user_profile=state.user_profile,
            intent=state.intent,
            ranked_products=[step.product for step in ritual.steps],
            knowledge=retrieved_knowledge,
            ritual=ritual,
            visual_observations=visual_observations,
            is_refinement=False,
            language_context=state.language_context
        )
        
        if prefix:
            raw_response = f"{prefix}\n\n{raw_response}"
            
        # Quality Gate
        from backend.engine.safety import validate_response
        safety_check = validate_response(raw_response)
        if safety_check.status == "UNSAFE":
            print("Quality Gate Failed (Safety). Regenerating deterministic safe response.")
            raw_response = "I've selected some gentle products that might help, but please consult a doctor if you have persistent concerns."
        
        # Word count check for brevity
        if len(raw_response.split()) > 200:
            print("Quality Gate Failed (Too Long). Regenerating shorter response.")
            # We don't want to block the user, so we fall back to a shorter version or let it pass with a warning, but user explicitly said "If any check fails: REGENERATE."
            raw_response = generate_response(
                user_profile=state.user_profile,
                intent=state.intent,
                ranked_products=[step.product for step in ritual.steps],
                knowledge=retrieved_knowledge,
                ritual=ritual,
                visual_observations=visual_observations,
                is_refinement=False,
                language_context=state.language_context
            ) # Generates a second time hoping it will be shorter due to strict instructions in generation prompt
            
        state.history.append({"role": "assistant", "content": raw_response})
        state.state = "RECOMMENDATION"
        
        return {
            "response": raw_response,
            "ritual": ritual.model_dump() if ritual else None,
            "visual_observations": visual_observations,
            "safety_status": state.safety_status,
            "developer_data": state.developer_data,
            "is_complete": True
        }
