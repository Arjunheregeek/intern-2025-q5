import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.api_client import GeminiAPIClient
from src.services.chatbot import RateLimitedChatbot

def main():
    """Start the rate limited chatbot demo."""
    try:
        print("🚀 Starting Rate Limited Chatbot Demo")
        
        # Initialize API client
        api_client = GeminiAPIClient()
        
        # Create rate limited chatbot (10 requests per minute)
        chatbot = RateLimitedChatbot(api_client, requests_per_minute=10)
        
        # Run chatbot
        chatbot.run()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
