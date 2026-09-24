"""
Chatbot Context Manager
=======================
Manages user context and conversation state for the chatbot.
Tracks selected college and other user preferences during conversation.
"""

from collections import OrderedDict


class ChatContext:
    """Manages conversation context for each user session."""
    
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.selected_college = None
        self.selected_course = None
        self.conversation_history = []
        self.last_query_intent = None
        
    def set_selected_college(self, college):
        """Set the college selected by user."""
        self.selected_college = college
        
    def get_selected_college(self):
        """Get the currently selected college."""
        return self.selected_college
        
    def set_selected_course(self, course):
        """Set the course selected by user."""
        self.selected_course = course
        
    def get_selected_course(self):
        """Get the currently selected course."""
        return self.selected_course
        
    def add_to_history(self, query, response):
        """Add query-response pair to conversation history.

        The history is capped at 50 entries by default to avoid unbounded growth.
        """
        self.conversation_history.append({
            'query': query,
            'response': response
        })
        # enforce cap of most recent 50
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
    def clear_context(self):
        """Clear all context for new conversation."""
        self.selected_college = None
        self.selected_course = None
        self.conversation_history = []
        self.last_query_intent = None


# Global context storage (in production, use Redis or database)
_user_contexts = {}


def get_user_context(user_id):
    """Get or create context for a user."""
    if user_id not in _user_contexts:
        _user_contexts[user_id] = ChatContext(user_id)
    return _user_contexts[user_id]


def clear_user_context(user_id):
    """Clear context for a user."""
    if user_id in _user_contexts:
        _user_contexts[user_id].clear_context()


def delete_user_context(user_id):
    """Delete complete context for a user."""
    if user_id in _user_contexts:
        del _user_contexts[user_id]
