import os
import sys
import time
import logging  # Add this missing import
import requests
from dotenv import load_dotenv
from prompt_template import TweetTemplate
from logging_config import setup_logging, get_logger
from retry_handler import retry_with_tenacity, RetryableHTTPError

# Initialize logging
setup_logging(log_level="INFO", log_file="tweet_generator.log")
logger = get_logger()

def force_log_flush():
    """Force flush all log handlers."""
    # Flush all loggers
    for name in logging.Logger.manager.loggerDict:
        log = logging.getLogger(name)
        for handler in log.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
    
    # Also flush root logger
    for handler in logging.getLogger().handlers:
        if hasattr(handler, 'flush'):
            handler.flush()

# Test initial logging with explicit file check
logger.info("=== APPLICATION STARTING ===")
force_log_flush()

# Check log file after initial write
import time
time.sleep(0.1)  # Brief pause to ensure file system sync

if os.path.exists("tweet_generator.log"):
    try:
        with open("tweet_generator.log", 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info("Log file status", exists=True, size=len(content), has_content=bool(content.strip()))
    except Exception as e:
        logger.error("Failed to read log file", error=str(e))
else:
    logger.error("Log file does not exist after initialization")

force_log_flush()

def call_gemini_api(prompt: str) -> str:
    """
    Make a call to Gemini API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        str: Generated response from the API
    """
    start_time = time.time()
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("API key not found", error="GEMINI_API_KEY not in environment")
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    logger.info(
        "Making API request",
        url_endpoint="gemini-1.5-flash",
        prompt_length=len(prompt),
        prompt_preview=prompt[:100] + "..." if len(prompt) > 100 else prompt
    )
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    generated_text = candidate['content']['parts'][0]['text'].strip()
                    
                    logger.info(
                        "API request successful",
                        status_code=response.status_code,
                        latency_ms=latency_ms,
                        response_length=len(generated_text),
                        response_preview=generated_text[:100] + "..." if len(generated_text) > 100 else generated_text
                    )
                    
                    return generated_text
                else:
                    error_msg = "Unexpected response structure in candidate content"
                    logger.error("API response parsing failed", error=error_msg, response_data=data)
                    raise Exception(error_msg)
            else:
                error_msg = "No candidates found in API response"
                logger.error("API response invalid", error=error_msg, response_data=data)
                raise Exception(error_msg)
        else:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            except:
                error_msg = response.text
            
            logger.error(
                "API request failed",
                status_code=response.status_code,
                latency_ms=latency_ms,
                error_message=error_msg
            )
            
            # Raise retryable error for 5xx status codes
            if 500 <= response.status_code < 600:
                raise RetryableHTTPError(response.status_code, error_msg)
            else:
                raise Exception(f"API Error {response.status_code}: {error_msg}")
            
    except requests.exceptions.Timeout:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error("API request timeout", latency_ms=latency_ms, timeout_seconds=30)
        raise
    except requests.exceptions.ConnectionError as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error("API connection failed", latency_ms=latency_ms, error=str(e))
        raise
    except requests.exceptions.RequestException as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.error("API request exception", latency_ms=latency_ms, error=str(e))
        raise Exception(f"Request failed: {e}")

def generate_tweet(topic: str, tone: str, max_words: int, max_retries: int = 3) -> str:
    """
    Generate a tweet using the template system and LLM API with retry logic.
    
    Args:
        topic (str): Tweet topic
        tone (str): Tone of the tweet
        max_words (int): Maximum number of words
        max_retries (int): Maximum retry attempts
        
    Returns:
        str: Generated tweet
    """
    logger.info(
        "Starting tweet generation",
        topic=topic,
        tone=tone,
        max_words=max_words,
        max_retries=max_retries
    )
    
    template = TweetTemplate()
    prompt = template.generate_tweet_prompt(topic, tone, max_words)
    
    # Use tenacity-based retry with logging
    try:
        result = retry_with_tenacity(
            lambda: call_gemini_api(prompt),  # Pass a lambda to ensure correct argument handling
            max_attempts=max_retries
        )
        
        logger.info(
            "Tweet generation successful",
            topic=topic,
            tone=tone,
            result_length=len(result)
        )
        
        return result
        
    except RetryableHTTPError as e:
        logger.error(
            "Tweet generation failed due to retryable error",
            topic=topic,
            tone=tone,
            error=str(e),
            max_retries=max_retries
        )
        raise
    except Exception as e:
        logger.error(
            "Tweet generation failed due to non-retryable error",
            topic=topic,
            tone=tone,
            error=str(e),
            max_retries=max_retries
        )
        raise

def main():
    """Demonstrate the enhanced tweet template system with logging and retries."""
    
    logger.info("Starting Tweet Template System Demo with Logging and Retries")
    force_log_flush()
    
    # Force flush logs to file periodically
    import logging
    
    examples = [
        {
            "topic": "Artificial Intelligence",
            "tone": "professional",
            "max_words": 25,
            "description": "Professional AI tweet"
        },
        {
            "topic": "Coffee",
            "tone": "humorous", 
            "max_words": 20,
            "description": "Humorous coffee tweet"
        },
        {
            "topic": "Remote Work",
            "tone": "casual",
            "max_words": 30,
            "description": "Casual remote work tweet"
        }
    ]
    
    # Generate tweets for each example
    for i, example in enumerate(examples, 1):
        logger.info(
            "Processing example",
            example_number=i,
            description=example['description'],
            parameters=example
        )
        
        print(f"Example {i}: {example['description']}")
        print(f"Topic: {example['topic']}")
        print(f"Tone: {example['tone']}")
        print(f"Max Words: {example['max_words']}")
        print("-" * 50)
        
        try:
            tweet = generate_tweet(
                topic=example['topic'],
                tone=example['tone'], 
                max_words=example['max_words'],
                max_retries=3
            )
            print(f"Generated Tweet:\n{tweet}")
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            logger.error("Example failed", example_number=i, error=str(e))
        
        # Force flush after each example
        force_log_flush()
        
        print("\n" + "="*60 + "\n")
    
    logger.info("=== Demo Completed Successfully ===")
    force_log_flush()

if __name__ == "__main__":
    main()