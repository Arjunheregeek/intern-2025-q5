import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.models.tweet_models import TweetResponse, TweetRequest, APIResponse

class TestTweetModels:
    """Test suite for dataclass models."""
    
    def test_valid_tweet_response(self):
        """Test valid tweet response creation."""
        response = TweetResponse(
            tweet="AI is transforming the world with innovative solutions!",
            word_count=9,
            sentiment="positive"
        )
        
        assert response.tweet == "AI is transforming the world with innovative solutions!"
        assert response.word_count == 9
        assert response.sentiment == "positive"
    
    def test_valid_tweet_request(self):
        """Test valid tweet request creation."""
        request = TweetRequest(
            topic="Artificial Intelligence",
            tone="professional",
            max_words=25
        )
        
        assert request.topic == "Artificial Intelligence"
        assert request.tone == "professional"
        assert request.max_words == 25
    
    def test_tweet_request_validation_errors(self):
        """Test tweet request validation."""
        # Short topic
        with pytest.raises(ValueError):
            TweetRequest(topic="A", tone="professional", max_words=25)
        
        # Invalid max_words
        with pytest.raises(ValueError):
            TweetRequest(topic="Valid Topic", tone="professional", max_words=100)
    
    def test_api_response_success(self):
        """Test successful API response."""
        tweet_data = TweetResponse(
            tweet="Test tweet content",
            word_count=3,
            sentiment="neutral"
        )
        
        response = APIResponse(
            success=True,
            data=tweet_data
        )
        
        assert response.success is True
        assert response.data == tweet_data
        assert response.error is None
    
    def test_api_response_error(self):
        """Test error API response."""
        response = APIResponse(
            success=False,
            error="Test error message"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.error == "Test error message"
