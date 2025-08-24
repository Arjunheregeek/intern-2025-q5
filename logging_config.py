import structlog
import logging
import sys
import os
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = "llm_requests.log"):
    """
    Configure structlog for structured logging to both console and file.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file (str): Path to log file
    """
    # Clear any existing configuration
    structlog.reset_defaults()
    
    # Ensure log file path exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove all existing handlers from root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set up file logging with a simple approach
    file_logger = logging.getLogger("file_logger")
    file_logger.handlers.clear()
    
    # Create file handler with explicit settings
    file_handler = logging.FileHandler(
        log_file, 
        mode='w',  # Overwrite file each time
        encoding='utf-8',
        delay=False  # Open immediately
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Simple formatter for both
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to different loggers
    file_logger.addHandler(file_handler)
    file_logger.setLevel(getattr(logging, log_level.upper()))
    
    root_logger.addHandler(console_handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Custom processor to write to file
    def write_to_file(logger, method_name, event_dict):
        # Format the log message
        message = structlog.dev.ConsoleRenderer(colors=False)(logger, method_name, event_dict)
        
        # Write to file logger
        getattr(file_logger, method_name.lower())(message)
        
        # Force flush immediately
        for handler in file_logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # Return the original event_dict to prevent "None" in console
        return event_dict
    
    # Configure structlog with dual output
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            write_to_file,  # Custom processor to write to file
            structlog.dev.ConsoleRenderer(colors=True),  # Console output
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    
    # Test the setup
    logger = structlog.get_logger()
    logger.info("=== LOGGING SYSTEM INITIALIZED ===", log_file=log_file, level=log_level)
    
    # Verify file was created
    if os.path.exists(log_file):
        logger.info("Log file created successfully", file_path=log_file)
        # Read back the file content to verify
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    logger.info("Log file verified writable and readable", content_length=len(content))
                else:
                    logger.error("Log file is empty after write test")
        except Exception as e:
            logger.error("Failed to read log file", error=str(e))
    else:
        logger.error("Log file was not created", expected_path=log_file)
    
    return logger

def get_logger():
    """Get configured structlog logger."""
    return structlog.get_logger()
