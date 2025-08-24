import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.services.rate_limiter import TokenBucket, RateLimiter

class TestTokenBucket:
    """Test token bucket algorithm."""
    
    def test_initial_state(self):
        """Test bucket starts full."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        status = bucket.get_status()
        
        assert status['current_tokens'] == 5
        assert status['capacity'] == 5
        assert bucket.consume(1) is True
    
    def test_token_consumption(self):
        """Test consuming tokens."""
        bucket = TokenBucket(capacity=3, refill_rate=1.0)
        
        # Consume tokens
        assert bucket.consume(1) is True
        assert bucket.consume(2) is True
        assert bucket.consume(1) is False  # Should fail - no tokens left
        
        status = bucket.get_status()
        assert status['current_tokens'] == 0
    
    def test_token_refill(self):
        """Test token refilling over time."""
        bucket = TokenBucket(capacity=2, refill_rate=2.0)  # 2 tokens per second
        
        # Consume all tokens
        bucket.consume(2)
        assert bucket.get_status()['current_tokens'] == 0
        
        # Wait for refill
        time.sleep(1.1)  # Wait longer than 1 second
        
        status = bucket.get_status()
        assert status['current_tokens'] >= 1.8  # Should have refilled
    
    def test_concurrent_access(self):
        """Test thread safety."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        results = []
        
        def consume_token():
            result = bucket.consume(1)
            results.append(result)
        
        # Create multiple threads
        threads = []
        for _ in range(15):  # More threads than capacity
            thread = threading.Thread(target=consume_token)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have exactly 10 successful consumptions
        successful = sum(1 for r in results if r)
        assert successful == 10
        assert len(results) == 15

class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_rate_limiting(self):
        """Test basic rate limiting."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 per second for testing
        
        # First request should be allowed
        assert limiter.is_allowed() is True
        
        # Rapid requests should be limited
        allowed_count = 0
        for _ in range(65):  # Try more than limit
            if limiter.is_allowed():
                allowed_count += 1
        
        # Should not exceed the bucket capacity
        assert allowed_count < 60
    
    def test_status_reporting(self):
        """Test rate limit status reporting."""
        limiter = RateLimiter(requests_per_minute=10)
        
        status = limiter.get_rate_limit_status()
        
        assert 'allowed' in status
        assert 'remaining_requests' in status
        assert 'limit_per_minute' in status
        assert 'reset_in_seconds' in status
        assert status['limit_per_minute'] == 10
    
    def test_time_until_reset(self):
        """Test reset time calculation."""
        limiter = RateLimiter(requests_per_minute=60)  # Fast refill for testing
        
        # Consume all tokens
        while limiter.is_allowed():
            pass
        
        reset_time = limiter.time_until_reset()
        assert reset_time > 0
        assert reset_time <= 1.0  # Should be less than 1 second for 60/min rate
