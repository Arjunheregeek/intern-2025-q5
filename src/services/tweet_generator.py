import json
from typing import Dict, Any
from pydantic import ValidationError
import structlog

from ..models.tweet_models import TweetResponse, APIResponse

logger = structlog.get_logger()

class JSONTweetGenerator:
    def __init__(self, api_client):
        self.api_client = api_client
        
    def generate_enhanced_prompt(self, topic: str, tone: str, max_words: int) -> str:
        """Enhanced prompt with strict JSON requirements and word counting."""
        return f"""You are a JSON-only API. Generate a {tone} tweet about "{topic}".

CRITICAL REQUIREMENTS:
1. Respond ONLY with valid JSON (no explanations, no markdown, no backticks)
2. Count words EXACTLY - be precise with the word_count field
3. Use exactly {max_words} words in the tweet

Required JSON format:
{{
    "tweet": "your tweet with exactly {max_words} words",
    "word_count": {max_words},
    "sentiment": "positive|negative|neutral"
}}

WORD COUNT EXAMPLE:
"AI is amazing" = 3 words
"The quick brown fox" = 4 words

Topic: {topic}
Tone: {tone}
Target words: {max_words}

JSON response:"""
    
    def validate_and_parse_response(self, raw_response: str) -> TweetResponse:
        """Parse and validate JSON response with Pydantic."""
        # Extract JSON
        start = raw_response.find('{')
        end = raw_response.rfind('}')
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        
        json_str = raw_response[start:end+1]
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        # Validate with Pydantic
        try:
            return TweetResponse(**data)
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {e}")
    
    def generate_tweet_with_retry(self, topic: str, tone: str, max_words: int, max_retries: int = 2) -> APIResponse:
        """Generate tweet with retry logic for validation failures."""
        retry_count = 0
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                prompt = self.generate_enhanced_prompt(topic, tone, max_words)
                raw_response = self.api_client.call_api(prompt)
                validated_tweet = self.validate_and_parse_response(raw_response)
                
                logger.info("Tweet generation successful", attempt=attempt + 1, retry_count=retry_count)
                
                return APIResponse(
                    success=True,
                    data=validated_tweet,
                    retry_count=retry_count
                )
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                logger.warning("Tweet generation failed", 
                             attempt=attempt + 1, 
                             error=last_error,
                             will_retry=attempt < max_retries)
                
                if attempt == max_retries:
                    break
        
        return APIResponse(
            success=False,
            error=f"Failed after {max_retries + 1} attempts: {last_error}",
            retry_count=retry_count
        )
    
    # Keep old method for compatibility
    def generate_tweet(self, topic: str, tone: str, max_words: int) -> Dict[str, Any]:
        """Legacy method - returns dict format."""
        result = self.generate_tweet_with_retry(topic, tone, max_words)
        
        if result.success:
            return {
                "success": True,
                "data": result.data.dict(),
                "error": None
            }
        else:
            return {
                "success": False,
                "data": None,
                "error": result.error
            }
