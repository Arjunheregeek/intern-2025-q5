import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import structlog
from src.models.tweet_models import TweetRequest
from src.services.api_client import GeminiAPIClient
from src.services.tweet_generator import JSONTweetGenerator

# Simple logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

def demo_validation_features():
    """Demonstrate validation and error handling."""
    logger.info("Testing Validation Features")
    
    api_client = GeminiAPIClient()
    generator = JSONTweetGenerator(api_client)
    
    # Test with retry logic
    print(f"\n{'='*60}")
    print("Testing Enhanced Validation with Retry Logic")
    print("="*60)
    
    test_case = ("Machine Learning", "professional", 15)
    topic, tone, max_words = test_case
    
    result = generator.generate_tweet_with_retry(topic, tone, max_words, max_retries=2)
    
    if result.success:
        print(f"✅ SUCCESS (after {result.retry_count} retries)")
        print(f"Tweet: {result.data.tweet}")
        print(f"Word Count: {result.data.word_count}")
        print(f"Sentiment: {result.data.sentiment}")
        print(f"Validation: PASSED")
    else:
        print(f"❌ FAILED after {result.retry_count} attempts")
        print(f"Error: {result.error}")

def main():
    """Enhanced demo with validation features."""
    logger.info("Starting Tweet Generator Demo")
    
    # Initialize
    api_client = GeminiAPIClient()
    generator = JSONTweetGenerator(api_client)
    
    # Test cases
    tests = [
        ("Artificial Intelligence", "professional", 25),
        ("Coffee", "humorous", 20),
        ("Remote Work", "casual", 30)
    ]
    
    for i, (topic, tone, max_words) in enumerate(tests, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {tone} tweet about {topic}")
        print("="*50)
        
        try:
            request = TweetRequest(topic=topic, tone=tone, max_words=max_words)
            result = generator.generate_tweet(request.topic, request.tone, request.max_words)
            
            if result["success"]:
                data = result["data"]
                print(f"✅ SUCCESS")
                print(f"Tweet: {data['tweet']}")
                print(f"Word Count: {data['word_count']}")
                print(f"Sentiment: {data['sentiment']}")
            else:
                print(f"❌ FAILED: {result['error']}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    # Add validation demo
    demo_validation_features()

if __name__ == "__main__":
    main()