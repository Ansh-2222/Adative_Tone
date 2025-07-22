import random
import json

class ToneEngine:
    """Generates responses with an adaptive tone."""

    def __init__(self, profile, memory_manager):
        self.profile = profile
        self.memory = memory_manager

    def _get_baseline_tone(self):
        """Gets the baseline tone from the user's profile."""
        # --- MODIFIED: Added default persona and humor ---
        return self.profile.get('tone_preferences', {
            "formality": "balanced",
            "enthusiasm": "medium",
            "verbosity": "balanced",
            "persona": "neutral",
            "humor": "none"
        })
    
    def _analyze_context(self, context):
        """Analyzes the conversation context to adjust the tone."""
        adjusted_tone = self._get_baseline_tone()
        # --- MODIFIED: Adjust persona and humor based on context ---
        if context == 'work':
            adjusted_tone['formality'] = 'professional'
            adjusted_tone['humor'] = 'none'
            adjusted_tone['persona'] = 'professional'
        elif context == 'personal':
            adjusted_tone['formality'] = 'casual'
            # For personal context, we rely on the user's baseline preferences for humor/persona
        return adjusted_tone

    def generate_response(self, message, context):
        """
        Generates a response by creating a prompt for an LLM.
        This is a simulation. In a real application, you would call an LLM API.
        """
        tone = self._analyze_context(context)
        
        prompt = f"You are a helpful assistant. Your current user prefers the following tone: {json.dumps(tone)}. "
        prompt += f"The conversation context is '{context}'. The user's technical level is '{self.profile.get('communication_style', {}).get('technical_level', 'intermediate')}'.\n\n"
        
        history = self.memory.get_conversation_history()
        for exchange in history:
            prompt += f"{exchange['role'].capitalize()}: {exchange['message']}\n"
        
        prompt += f"User: {message}\nAssistant:"
        
        print("--- GENERATED PROMPT ---")
        print(prompt)
        print("------------------------")

        simulated_response = self._get_simulated_llm_response(message, tone)

        return simulated_response, tone

    def _get_simulated_llm_response(self, message, tone):
        """Simulates a response from an LLM based on the tone."""
        responses = {
            "casual": f"Hey there! So, about '{message}', you could probably just...",
            "professional": f"Regarding your query about '{message}', the recommended course of action is...",
            "formal": f"With respect to your inquiry, '{message}', it is advisable to proceed by..."
        }
        
        base_response = responses.get(tone.get('formality', 'casual'), "I'm not sure how to answer that.")

        if tone.get('enthusiasm') == 'high':
            base_response += " It's going to be absolutely fantastic!"
        if tone.get('verbosity') == 'detailed':
            base_response += " To elaborate further, this involves several steps starting with..."
        
        # --- NEW: Add persona and humor to the response ---
        personas = {
            "witty": " You know, a clever person might say that...",
            "friendly": " Just a friendly thought here, but...",
            "professional": " From a professional standpoint, it's clear that..."
        }
        base_response += personas.get(tone.get('persona', 'neutral'), "")

        if tone.get('humor') == 'punny':
            puns = [" That's a *punny* way to put it!", " I'm not *kitten* you, that's the answer.", " That's some *egg-cellent* logic!"]
            base_response += random.choice(puns)
        
        return base_response

    def process_feedback(self, feedback_type):
        """Adjusts user profile based on feedback."""
        history = self.profile.get('interaction_history', {})
        score = history.get('feedback_score', 0)

        if feedback_type == 'positive':
            score += 1
            history['successful_tone_matches'] = history.get('successful_tone_matches', 0) + 1
        elif feedback_type == 'negative':
            score -= 1
        
        history['feedback_score'] = score
        self.profile['interaction_history'] = history
        print(f"Feedback processed. New score: {score}")