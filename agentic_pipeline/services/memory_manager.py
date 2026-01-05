"""
Memory Manager
==============
Manages conversation history and resolves entity references.
"""

from typing import List, Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryManager:
    """
    Manages conversation history and resolves references.
    
    This class maintains conversation context and resolves pronouns
    like "it", "them", "that vessel" to actual entity references.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the memory manager.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []
        self.last_mentioned_vessels: List[str] = []
        self.last_intent: Optional[str] = None
    
    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        logger.debug(f"Added {role} message to history")
    
    def get_recent_context(self, n: int = 5) -> List[Dict[str, str]]:
        """
        Get the last N messages from history.
        
        Args:
            n: Number of recent messages to retrieve
            
        Returns:
            List of recent messages
        """
        return self.conversation_history[-n:]
    
    def update_vessel_context(self, vessels: List[str]):
        """
        Update the list of last mentioned vessels.
        
        Args:
            vessels: List of vessel IDs/MMSIs
        """
        if vessels:
            self.last_mentioned_vessels = vessels
            logger.debug(f"Updated vessel context: {vessels}")
    
    def update_intent_context(self, intent: str):
        """
        Update the last mentioned intent.
        
        Args:
            intent: Intent string
        """
        self.last_intent = intent
        logger.debug(f"Updated intent context: {intent}")
    
    def resolve_references(self, query: str) -> Dict[str, any]:
        """
        Resolve pronoun references in the query.
        
        This method identifies pronouns and references in the query
        and maps them to entities from conversation context.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with resolved references
            
        Example:
            >>> mm = MemoryManager()
            >>> mm.update_vessel_context(["123456789"])
            >>> resolved = mm.resolve_references("Show its trajectory")
            >>> print(resolved)
            {'vessels': ['123456789'], 'has_reference': True}
        """
        query_lower = query.lower()
        resolved = {
            "vessels": [],
            "intent": None,
            "has_reference": False
        }
        
        # Check for pronoun references
        pronouns = ["it", "its", "them", "their", "that vessel", "those vessels", "the vessel", "the ship"]
        has_pronoun = any(pronoun in query_lower for pronoun in pronouns)
        
        if has_pronoun and self.last_mentioned_vessels:
            resolved["vessels"] = self.last_mentioned_vessels
            resolved["has_reference"] = True
            logger.info(f"Resolved pronoun reference to vessels: {self.last_mentioned_vessels}")
        
        # Check for intent references
        intent_refs = ["same", "again", "also"]
        if any(ref in query_lower for ref in intent_refs) and self.last_intent:
            resolved["intent"] = self.last_intent
            resolved["has_reference"] = True
            logger.info(f"Resolved intent reference to: {self.last_intent}")
        
        return resolved
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the current context.
        
        Returns:
            String summary of context
        """
        summary_parts = []
        
        if self.last_mentioned_vessels:
            summary_parts.append(f"Last vessels: {', '.join(self.last_mentioned_vessels)}")
        
        if self.last_intent:
            summary_parts.append(f"Last intent: {self.last_intent}")
        
        summary_parts.append(f"History length: {len(self.conversation_history)}")
        
        return " | ".join(summary_parts)
    
    def clear(self):
        """Clear all conversation history and context."""
        self.conversation_history = []
        self.last_mentioned_vessels = []
        self.last_intent = None
        logger.info("Memory cleared")
