import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.services.memory_manager import ConversationMemoryManager

class TestMemoryManager:
    """Test suite for conversation memory functionality."""
    
    def test_memory_initialization(self):
        """Test memory manager initialization."""
        manager = ConversationMemoryManager(window_size=4)
        status = manager.get_memory_status()
        
        assert status['total_messages'] == 0
        assert status['conversation_turns'] == 0
        assert status['current_turn'] == 0
        assert status['memory_window_size'] == 4
        assert status['is_memory_full'] is False
    
    def test_add_messages(self):
        """Test adding user and AI messages."""
        manager = ConversationMemoryManager(window_size=2)
        
        manager.add_user_message("Hello")
        manager.add_ai_message("Hi there!")
        
        status = manager.get_memory_status()
        assert status['total_messages'] == 2
        assert status['conversation_turns'] == 1
        assert status['current_turn'] == 1
    
    def test_memory_window_sliding(self):
        """Test that memory window slides correctly."""
        manager = ConversationMemoryManager(window_size=2)
        
        # Add 3 conversation turns (6 messages)
        for i in range(3):
            manager.add_user_message(f"User message {i+1}")
            manager.add_ai_message(f"AI response {i+1}")
        
        status = manager.get_memory_status()
        history = manager.get_conversation_history()
        
        # Should only keep last 2 turns (4 messages)
        assert status['total_messages'] == 4
        assert status['conversation_turns'] == 2
        assert status['is_memory_full'] is True
        
        # Check that oldest messages were removed
        assert "User message 1" not in str(history)
        assert "User message 2" in str(history)
        assert "User message 3" in str(history)
    
    def test_clear_memory(self):
        """Test clearing conversation memory."""
        manager = ConversationMemoryManager(window_size=4)
        
        manager.add_user_message("Test message")
        manager.add_ai_message("Test response")
        
        assert manager.get_memory_status()['total_messages'] == 2
        
        manager.clear_memory()
        
        status = manager.get_memory_status()
        assert status['total_messages'] == 0
        assert status['current_turn'] == 0
    
    def test_conversation_context_formatting(self):
        """Test LLM context formatting."""
        manager = ConversationMemoryManager(window_size=4)
        
        manager.add_user_message("What is AI?")
        manager.add_ai_message("AI stands for Artificial Intelligence.")
        manager.add_user_message("Tell me more")
        manager.add_ai_message("AI involves machine learning and neural networks.")
        
        context = manager.get_context_for_llm()
        
        assert "User: What is AI?" in context
        assert "Assistant: AI stands for Artificial Intelligence." in context
        assert "User: Tell me more" in context
        assert "Assistant: AI involves machine learning and neural networks." in context
