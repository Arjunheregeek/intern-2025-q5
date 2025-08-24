from pydantic import BaseModel, Field, validator
from typing import Literal, Optional

class TweetResponse(BaseModel):
    """Pydantic model with strict validation."""
    tweet: str = Field(..., min_length=1, max_length=280)
    word_count: int = Field(..., gt=0)
    sentiment: Literal["positive", "negative", "neutral"]
    
    @validator('word_count')
    def validate_word_count_accuracy(cls, v, values):
        """Ensure word count matches actual tweet words."""
        if 'tweet' in values:
            actual_count = len(values['tweet'].split())
            if abs(v - actual_count) > 2:  # Allow ±2 variance
                raise ValueError(f"Word count mismatch: claimed {v}, actual {actual_count}")
        return v
    
    @validator('tweet')
    def validate_tweet_content(cls, v):
        """Basic tweet content validation."""
        if not v.strip():
            raise ValueError("Tweet cannot be empty")
        return v.strip()

class TweetRequest(BaseModel):
    """Enhanced request model."""
    topic: str = Field(..., min_length=2, max_length=100)
    tone: Literal["professional", "humorous", "casual", "excited", "informative", "sarcastic"]
    max_words: int = Field(..., ge=5, le=50)

class APIResponse(BaseModel):
    """API response wrapper."""
    success: bool
    data: Optional[TweetResponse] = None
    error: Optional[str] = None
    retry_count: int = 0
