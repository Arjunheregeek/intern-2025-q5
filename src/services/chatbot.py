import sys
from typing import Optional
import structlog
from .memory_manager import ConversationMemoryManager
from .api_client import GeminiAPIClient

logger = structlog.get_logger()

class CLIChatbot:
    """Interactive CLI chatbot with conversation memory."""
    
    def __init__(self, api_client: GeminiAPIClient):
        """Initialize chatbot with API client."""
        self.api_client = api_client
        self.memory_manager = ConversationMemoryManager(window_size=4)
        self.is_running = False
        
    def display_welcome(self) -> None:
        """Display welcome message and commands."""
        print("\n" + "="*60)
        print("🤖 AI CHATBOT WITH MEMORY")
        print("="*60)
        print("I can remember our last 4 conversation turns!")
        print("\nAvailable commands:")
        print("  • 'quit' or 'exit' - End the conversation")
        print("  • 'clear' - Clear conversation history")
        print("  • 'history' - Show conversation history")
        print("  • 'status' - Show memory buffer status")
        print("\nStart chatting! Type your message and press Enter.")
        print("="*60)
    
    def display_memory_status(self) -> None:
        """Display current memory buffer status."""
        status = self.memory_manager.get_memory_status()
        print(f"\n📊 Memory Status:")
        print(f"  • Current turn: {status['current_turn']}")
        print(f"  • Messages in buffer: {status['total_messages']}")
        print(f"  • Conversation turns: {status['conversation_turns']}")
        print(f"  • Memory window: {status['memory_window_size']} turns")
        print(f"  • Buffer full: {'Yes' if status['is_memory_full'] else 'No'}")
    
    def display_conversation_history(self) -> None:
        """Display formatted conversation history."""
        history = self.memory_manager.get_conversation_history()
        
        if not history:
            print("\n📝 No conversation history yet.")
            return
        
        print("\n📝 Conversation History:")
        print("-" * 50)
        
        current_turn = None
        for msg in history:
            if msg['turn'] != current_turn:
                current_turn = msg['turn']
                print(f"\nTurn {current_turn}:")
            
            role_icon = "👤" if msg['role'] == "user" else "🤖"
            role_name = "You" if msg['role'] == "user" else "AI"
            print(f"  {role_icon} {role_name}: {msg['content']}")
        
        print("-" * 50)
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate AI response with conversation context."""
        try:
            # Build prompt with conversation context
            context = self.memory_manager.get_context_for_llm()
            
            if context:
                prompt = f"""You are a helpful AI assistant having a conversation. Here's our conversation history:

{context}

User: {user_input}

Please provide a natural, helpful response that takes into account our conversation history. Keep your response concise and engaging."""
            else:
                prompt = f"""You are a helpful AI assistant. The user said: {user_input}

Please provide a natural, helpful response. Keep it concise and engaging."""
            
            logger.info("Generating response", user_input_length=len(user_input), has_context=bool(context))
            
            response = self.api_client.call_api(prompt)
            
            logger.info("Response generated successfully", response_length=len(response))
            return response
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            logger.error("Failed to generate response", error=str(e))
            return error_msg
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit']:
            print("\n👋 Goodbye! Thanks for chatting!")
            return True
        
        elif command == 'clear':
            self.memory_manager.clear_memory()
            print("\n🧹 Conversation history cleared!")
            return True
        
        elif command == 'history':
            self.display_conversation_history()
            return True
        
        elif command == 'status':
            self.display_memory_status()
            return True
        
        return False
    
    def run(self) -> None:
        """Start the interactive CLI chatbot."""
        self.display_welcome()
        self.is_running = True
        
        try:
            while self.is_running:
                # Get user input
                try:
                    user_input = input(f"\n[Turn {self.memory_manager.turn_number + 1}] You: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self.handle_command(user_input):
                    if user_input.lower().strip() in ['quit', 'exit']:
                        break
                    continue
                
                # Add user message to memory
                self.memory_manager.add_user_message(user_input)
                
                # Generate and display AI response
                print(f"\n🤖 AI: ", end="", flush=True)
                response = self.generate_response(user_input)
                
                if response:
                    print(response)
                    # Add AI response to memory
                    self.memory_manager.add_ai_message(response)
                else:
                    print("I'm having trouble right now. Please try again.")
        
        except Exception as e:
            logger.error("Chatbot error", error=str(e))
            print(f"\n❌ An unexpected error occurred: {e}")
        
        finally:
            self.is_running = False
