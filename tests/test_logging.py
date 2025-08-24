import pytest
import tempfile
import os
import sys
import json

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import setup_logging, get_logger

class TestLogging:
    """Test suite for logging configuration."""
    
    def test_logger_setup(self):
        """Test that logger is properly configured."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_log:
            temp_log_path = temp_log.name
        
        try:
            logger = setup_logging(log_level="INFO", log_file=temp_log_path)
            assert logger is not None
            
            # Test logging with explicit flush
            logger.info("Test message", test_key="test_value")
            
            # Force flush all handlers
            import logging
            for handler in logging.getLogger().handlers:
                handler.flush()
            
            # Verify log file exists and has content
            assert os.path.exists(temp_log_path)
            
            with open(temp_log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
                assert "Test message" in log_content
                assert "test_key" in log_content
                
        finally:
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)
    
    def test_get_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger()
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
    
    def test_structured_logging(self):
        """Test that structured data is properly logged."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_log:
            temp_log_path = temp_log.name
        
        try:
            logger = setup_logging(log_level="DEBUG", log_file=temp_log_path)
            
            # Log structured data
            logger.info(
                "API request",
                method="POST",
                url="https://api.example.com",
                status_code=200,
                latency_ms=150.5
            )
            
            # Read and verify log content
            with open(temp_log_path, 'r') as f:
                log_lines = f.readlines()
                assert len(log_lines) > 0
                
                # Should contain structured data
                log_content = ''.join(log_lines)
                assert "API request" in log_content
                assert "method" in log_content
                assert "latency_ms" in log_content
                
        finally:
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)
