import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import structlog
from src.services.api_client import GeminiAPIClient
from src.services.chatbot import CLIChatbot

# Simple logging setup
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

def main():
    """Start the CLI chatbot with conversation memory."""
    try:
        logger.info("Starting CLI Chatbot with Memory")
        
        # Initialize API client
        api_client = GeminiAPIClient()
        
        # Create and run chatbot
        chatbot = CLIChatbot(api_client)
        chatbot.run()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error("Application error", error=str(e))
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
