import threading
import time
from typing import Dict, Any

class TokenBucket:
    """Thread-safe token bucket implementation for rate limiting."""
    
    def __init__(self, capacity: int = 10, refill_rate: float = 10/60):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens (default: 10)
            refill_rate: Tokens per second (default: 10 tokens per 60 seconds)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)  # Start with full bucket
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time. Called with lock held."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if rate limited
        """
        with self.lock:
            self._refill_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bucket status."""
        with self.lock:
            self._refill_tokens()
            
            # Calculate time until next token
            time_per_token = 1.0 / self.refill_rate if self.refill_rate > 0 else 0
            tokens_needed = max(0, 1 - self.tokens)
            next_token_time = tokens_needed * time_per_token
            
            return {
                "current_tokens": round(self.tokens, 2),
                "capacity": self.capacity,
                "refill_rate_per_minute": round(self.refill_rate * 60, 2),
                "next_token_in_seconds": round(next_token_time, 1) if next_token_time > 0 else 0,
                "bucket_full": self.tokens >= self.capacity
            }
    
    def time_until_available(self, tokens: int = 1) -> float:
        """Calculate seconds until requested tokens are available."""
        with self.lock:
            self._refill_tokens()
            
            if self.tokens >= tokens:
                return 0.0
            
            tokens_needed = tokens - self.tokens
            return tokens_needed / self.refill_rate if self.refill_rate > 0 else float('inf')

class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.bucket = TokenBucket(
            capacity=requests_per_minute,
            refill_rate=requests_per_minute / 60.0  # Convert to per-second
        )
        self.requests_per_minute = requests_per_minute
    
    def is_allowed(self) -> bool:
        """Check if request is allowed (consumes 1 token)."""
        return self.bucket.consume(1)
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get detailed rate limit status."""
        status = self.bucket.get_status()
        return {
            "allowed": status["current_tokens"] >= 1,
            "remaining_requests": int(status["current_tokens"]),
            "limit_per_minute": self.requests_per_minute,
            "reset_in_seconds": status["next_token_in_seconds"],
            "bucket_status": status
        }
    
    def time_until_reset(self) -> float:
        """Get seconds until next request is allowed."""
        return self.bucket.time_until_available(1)
