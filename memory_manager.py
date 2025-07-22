from collections import deque
import json

class MemoryManager:
    """Manages a user's short-term and long-term memory."""

    def __init__(self, user_id, profile):
        self.user_id = user_id
        self.profile = profile
        self.short_term_memory = deque(maxlen=20) 
        self.tone_patterns = {} 
        self.context_embeddings = {} 
        self._load_long_term_memory()

    def _load_long_term_memory(self):
        """Loads relevant long-term memory aspects into the manager."""
        if self.profile and 'interaction_history' in self.profile:
            self.tone_patterns = self.profile.get('successful_tone_patterns', {})

    def add_to_short_term_memory(self, exchange):
        """Adds a conversation exchange to short-term memory."""
        self.short_term_memory.append(exchange)

    def get_conversation_history(self):
        """Returns the recent conversation history."""
        return list(self.short_term_memory)

    def clear_short_term_memory(self):
        """Clears the short-term memory buffer."""
        self.short_term_memory.clear()

    def update_tone_pattern(self, context, tone):
        """Updates a successful tone pattern for a given context."""
        self.tone_patterns[context] = tone
        print(f"Updated tone pattern for {context}: {tone}")

    def get_context_embedding(self, context):
        """Retrieves a stored embedding for a context."""
        return self.context_embeddings.get(context)

    def update_context_embedding(self, context, vector):
        """Updates or adds a context embedding."""
        self.context_embeddings[context] = vector