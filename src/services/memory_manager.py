from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()

class ConversationMemoryManager:
    """Manages conversation memory using LangChain ConversationBufferWindowMemory."""
    
    def __init__(self, window_size: int = 4):
        """
        Initialize memory manager with sliding window.
        
        Args:
            window_size: Number of conversation turns to remember (default: 4)
        """
        self.memory = ConversationBufferWindowMemory(
            k=window_size,  # Keep last 4 turns (8 messages total)
            return_messages=True,
            memory_key="chat_history"
        )
        self.turn_number = 0
        logger.info("Memory manager initialized", window_size=window_size)
    
    def add_user_message(self, message: str) -> None:
        """Add user message to memory."""
        self.memory.chat_memory.add_user_message(message)
        self.turn_number += 1
        logger.debug("User message added", turn=self.turn_number, message_length=len(message))
    
    def add_ai_message(self, message: str) -> None:
        """Add AI response to memory."""
        self.memory.chat_memory.add_ai_message(message)
        logger.debug("AI message added", turn=self.turn_number, message_length=len(message))
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get formatted conversation history."""
        messages = self.memory.chat_memory.messages
        history = []
        
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                history.append({
                    "role": "user",
                    "content": msg.content,
                    "turn": (i // 2) + 1
                })
            elif isinstance(msg, AIMessage):
                history.append({
                    "role": "assistant", 
                    "content": msg.content,
                    "turn": (i // 2) + 1
                })
        
        return history
    
    def get_context_for_llm(self) -> str:
        """Get conversation context formatted for LLM prompt."""
        messages = self.memory.chat_memory.messages
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                context_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                context_parts.append(f"Assistant: {msg.content}")
        
        return "\n".join(context_parts)
    
    def clear_memory(self) -> None:
        """Clear all conversation history."""
        old_turn_count = self.turn_number
        self.memory.clear()
        self.turn_number = 0
        logger.info("Memory cleared", previous_turns=old_turn_count)
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory buffer status."""
        messages = self.memory.chat_memory.messages
        return {
            "total_messages": len(messages),
            "conversation_turns": len(messages) // 2,
            "current_turn": self.turn_number,
            "memory_window_size": self.memory.k,
            "is_memory_full": len(messages) >= (self.memory.k * 2)
        }
