import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from pydantic import ValidationError
from src.models.tweet_models import TweetResponse, TweetRequest
from src.services.tweet_generator import JSONTweetGenerator

class TestValidation:
    """Test validation edge cases and error handling."""
    
    def test_tweet_response_validation(self):
        """Test Pydantic validation rules."""
        # Valid case
        valid_tweet = TweetResponse(
            tweet="AI is amazing",
            word_count=3,
            sentiment="positive"
        )
        assert valid_tweet.word_count == 3
        
        # Invalid sentiment
        with pytest.raises(ValidationError):
            TweetResponse(
                tweet="Test tweet",
                word_count=2,
                sentiment="invalid"
            )
        
        # Word count mismatch
        with pytest.raises(ValidationError):
            TweetResponse(
                tweet="This has five words exactly",
                word_count=10,  # Should be 5
                sentiment="neutral"
            )
    
    def test_json_extraction_errors(self):
        """Test JSON parsing error cases."""
        generator = JSONTweetGenerator(None)  # Mock client
        
        # No JSON
        with pytest.raises(ValueError, match="No JSON found"):
            generator.validate_and_parse_response("Just text, no JSON")
        
        # Malformed JSON
        with pytest.raises(ValueError, match="Invalid JSON format"):
            generator.validate_and_parse_response('{"tweet": "test", "incomplete":}')
        
        # Missing required fields
        with pytest.raises(ValueError, match="Schema validation failed"):
            generator.validate_and_parse_response('{"tweet": "test"}')  # Missing word_count, sentiment
