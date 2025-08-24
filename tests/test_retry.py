import pytest
import requests
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from retry_handler import retry_with_tenacity, retry_with_custom_backoff, RetryableHTTPError, is_retryable_error

class TestRetryLogic:
    """Test suite for retry functionality."""
    
    def test_is_retryable_error_5xx(self):
        """Test that 5xx errors are considered retryable."""
        error = RetryableHTTPError(500, "Internal Server Error")
        assert is_retryable_error(error) is True
        
        error = RetryableHTTPError(503, "Service Unavailable")
        assert is_retryable_error(error) is True
    
    def test_is_retryable_error_4xx(self):
        """Test that 4xx errors are not retryable."""
        error = RetryableHTTPError(400, "Bad Request")
        assert is_retryable_error(error) is False
        
        error = RetryableHTTPError(404, "Not Found")
        assert is_retryable_error(error) is False
    
    def test_connection_errors_retryable(self):
        """Test that connection errors are retryable."""
        error = requests.exceptions.ConnectionError("Connection failed")
        assert is_retryable_error(error) is True
        
        error = requests.exceptions.Timeout("Request timeout")
        assert is_retryable_error(error) is True
    
    def test_tenacity_retry_success_first_attempt(self):
        """Test successful function call on first attempt."""
        mock_func = Mock(return_value="success")
        
        result = retry_with_tenacity(mock_func, max_attempts=3)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_tenacity_retry_success_after_retries(self):
        """Test successful function call after retries."""
        mock_func = Mock(side_effect=[
            RetryableHTTPError(500, "Server Error"),
            RetryableHTTPError(503, "Service Unavailable"),
            "success"
        ])
        
        result = retry_with_tenacity(mock_func, max_attempts=3)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_tenacity_retry_max_attempts_exceeded(self):
        """Test that max attempts are respected."""
        mock_func = Mock(side_effect=RetryableHTTPError(500, "Server Error"))
        
        with pytest.raises(RetryableHTTPError):
            retry_with_tenacity(mock_func, max_attempts=2)
        
        assert mock_func.call_count == 2
    
    def test_custom_retry_success_first_attempt(self):
        """Test custom retry logic with immediate success."""
        mock_func = Mock(return_value="success")
        
        result = retry_with_custom_backoff(mock_func, max_attempts=3)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    @patch('time.sleep')
    def test_custom_retry_with_delays(self, mock_sleep):
        """Test custom retry logic respects delays."""
        mock_func = Mock(side_effect=[
            RetryableHTTPError(500, "Server Error"),
            "success"
        ])
        
        result = retry_with_custom_backoff(mock_func, max_attempts=3, base_delay=1.0)
        
        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once()  # Should sleep once between attempts
    
    def test_non_retryable_error_no_retry(self):
        """Test that non-retryable errors are not retried."""
        mock_func = Mock(side_effect=RetryableHTTPError(400, "Bad Request"))
        
        with pytest.raises(RetryableHTTPError):
            retry_with_custom_backoff(mock_func, max_attempts=3)
        
        assert mock_func.call_count == 1  # Should not retry
