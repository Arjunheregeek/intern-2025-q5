import sys
import time
from typing import Optional
from .api_client import GeminiAPIClient
from .rate_limiter import RateLimiter

class RateLimitedChatbot:
    """CLI chatbot with token bucket rate limiting."""
    
    def __init__(self, api_client: GeminiAPIClient, requests_per_minute: int = 10):
        """Initialize chatbot with rate limiter."""
        self.api_client = api_client
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.is_running = False
        self.message_count = 0
    
    def display_welcome(self) -> None:
        """Display welcome message with rate limit info."""
        print("\n" + "="*60)
        print("🤖 RATE LIMITED CHATBOT")
        print("="*60)
        print(f"Rate limit: {self.rate_limiter.requests_per_minute} messages per minute")
        print("\nAvailable commands:")
        print("  • 'quit' or 'exit' - End the conversation")
        print("  • 'status' - Show rate limit status")
        print("  • 'rapid' - Test rapid requests (demo rate limiting)")
        print("\nStart chatting! Rate limits will be enforced.")
        print("="*60)
    
    def display_rate_limit_status(self) -> None:
        """Display current rate limit status."""
        status = self.rate_limiter.get_rate_limit_status()
        print(f"\n📊 Rate Limit Status:")
        print(f"  • Remaining requests: {status['remaining_requests']}")
        print(f"  • Limit per minute: {status['limit_per_minute']}")
        print(f"  • Next token in: {status['reset_in_seconds']}s")
        print(f"  • Request allowed: {'✅ Yes' if status['allowed'] else '❌ No'}")
        
        bucket = status['bucket_status']
        print(f"  • Bucket tokens: {bucket['current_tokens']}/{bucket['capacity']}")
        print(f"  • Refill rate: {bucket['refill_rate_per_minute']} tokens/min")
    
    def handle_rate_limit(self) -> bool:
        """Handle rate limit exceeded. Returns True to continue, False to quit."""
        status = self.rate_limiter.get_rate_limit_status()
        reset_time = status['reset_in_seconds']
        
        print(f"\n⚠️  Rate limit exceeded!")
        print(f"Please wait {reset_time:.1f} seconds for next request.")
        print("Commands: 'status', 'quit', or wait for rate limit reset")
        
        return True
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate AI response with rate limiting."""
        # Check rate limit first
        if not self.rate_limiter.is_allowed():
            return None  # Rate limited
        
        try:
            prompt = f"You are a helpful assistant. User said: {user_input}\n\nProvide a helpful response:"
            response = self.api_client.call_api(prompt)
            self.message_count += 1
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit']:
            print("\n👋 Goodbye!")
            return True
        
        elif command == 'status':
            self.display_rate_limit_status()
            return True
        
        elif command == 'rapid':
            self.demo_rapid_requests()
            return True
        
        return False
    
    def demo_rapid_requests(self) -> None:
        """Demo rapid requests to show rate limiting."""
        print("\n🚀 Rapid Request Demo (testing rate limits)...")
        
        for i in range(5):
            print(f"\nRequest {i+1}: ", end="", flush=True)
            
            if self.rate_limiter.is_allowed():
                print("✅ Allowed")
            else:
                status = self.rate_limiter.get_rate_limit_status()
                print(f"❌ Rate limited (wait {status['reset_in_seconds']:.1f}s)")
            
            time.sleep(0.5)  # Small delay between requests
        
        self.display_rate_limit_status()
    
    def get_prompt_with_tokens(self) -> str:
        """Get input prompt showing available tokens."""
        status = self.rate_limiter.get_rate_limit_status()
        remaining = status['remaining_requests']
        
        if remaining > 0:
            return f"\n[Tokens: {remaining}] You: "
        else:
            reset_time = status['reset_in_seconds']
            return f"\n[Rate Limited - wait {reset_time:.1f}s] You: "
    
    def run(self) -> None:
        """Start the rate limited chatbot."""
        self.display_welcome()
        self.is_running = True
        
        try:
            while self.is_running:
                # Get user input with token status
                try:
                    user_input = input(self.get_prompt_with_tokens()).strip()
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
                
                # Try to generate response
                response = self.generate_response(user_input)
                
                if response is None:
                    # Rate limited
                    if not self.handle_rate_limit():
                        break
                    continue
                
                # Display response
                print(f"\n🤖 AI: {response}")
        
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
        
        finally:
            self.is_running = False
            print(f"\nTotal messages sent: {self.message_count}")
