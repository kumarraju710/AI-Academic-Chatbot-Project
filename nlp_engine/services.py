import os

# Response mechanism uses the enhanced context-aware engine in ``chatbot_v3.py``.
# This provides deterministic, structured responses with session context management
# and support for college tracking, fee structures, and detailed information.
from .chatbot_v3 import get_bot_response



def generate_response(text, user_id=None):
    """Return a reply for the user input with context awareness.

    The chatbot uses a fully deterministic, JSON-driven engine which guarantees
    accurate replies for all colleges, courses, fees, and other information.
    
    Context management (chatbot_context.py) tracks user selections like preferred
    college across conversation sessions for personalized responses.

    Args:
        text: User message
        user_id: Optional user ID for context tracking
        
    Returns:
        Formatted response string
    """
    return get_bot_response(text, user_id)
