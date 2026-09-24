"""
Chatbot Services - Enhanced Context-Aware Response Generation
=============================================================

Uses JSON-based rule engine with session context management.
Provides deterministic, accurate responses with user preferences.
"""

from .chatbot_v3 import get_bot_response as get_v3_response


def generate_response(text, user_id=None):
    """Generate response from user text with context awareness.
    
    Returns response strictly from JSON data sources.
    Uses context management to track selected college per user.
    
    Args:
        text: User message
        user_id: Optional user ID for context tracking
    
    Returns:
        Formatted response string
    """
    return get_v3_response(text, user_id)
