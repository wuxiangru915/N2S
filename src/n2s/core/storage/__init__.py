"""
Storage domain.

This module provides the core abstractions for conversation storage in the N2S Agent framework.
"""

from .base import ConversationStore
from .models import Conversation, Message

__all__ = [
    "ConversationStore",
    "Conversation",
    "Message",
]
