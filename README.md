# Enhanced Tweet Generator with Logging and Retry Logic

A production-ready tweet generator with comprehensive logging, exponential backoff retry logic, and error resilience. Built on the Q2 template system with enterprise-grade reliability features.

## New Features in Q3

- ✅ **Structured Logging**: JSON-formatted logs with structlog
- ✅ **Exponential Backoff Retry**: Automatic retry for transient failures
- ✅ **Dual Logging Output**: Console and file logging
- ✅ **Request/Response Tracking**: Full API call telemetry
- ✅ **Configurable Retry Logic**: Customizable retry attempts and delays
- ✅ **Comprehensive Testing**: Unit tests for retry and logging

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

## Usage

### Basic Tweet Generation with Logging

```python
from main import generate_tweet
from logging_config import setup_logging

# Initialize logging
setup_logging(log_level="INFO", log_file="tweets.log")

# Generate tweet with automatic retries
tweet = generate_tweet(
    topic="Python Programming",
    tone="professional",
    max_words=25,
    max_retries=3
)
print(tweet)
```

### Retry Configuration

```python
from retry_handler import retry_with_tenacity, retry_with_custom_backoff

# Using tenacity library (recommended)
result = retry_with_tenacity(
    your_function,
    max_attempts=3,
    base_delay=1.0,
    max_delay=10.0
)

# Using custom implementation
result = retry_with_custom_backoff(
    your_function,
    max_attempts=3,
    base_delay=1.0
)
```

## Demo Output

Run the enhanced demo:
```bash
python main.py
```

### Normal Operation Logs

```json
{
  "event": "Making API request",
  "level": "info",
  "timestamp": "2024-08-24T16:04:23.123456Z",
  "url_endpoint": "gemini-1.5-flash",
  "prompt_length": 87,
  "prompt_preview": "Generate a professional tweet about Artificial Intelligence..."
}

{
  "event": "API request successful", 
  "level": "info",
  "timestamp": "2024-08-24T16:04:23.456789Z",
  "status_code": 200,
  "latency_ms": 333.33,
  "response_length": 156,
  "response_preview": "Artificial Intelligence is transforming industries..."
}
```

### Retry Behavior Logs

```json
{
  "event": "API request failed",
  "level": "error", 
  "timestamp": "2024-08-24T16:04:23.789012Z",
  "status_code": 503,
  "latency_ms": 5000.0,
  "error_message": "Service temporarily unavailable"
}

{
  "event": "Retry attempt",
  "level": "warning",
  "timestamp": "2024-08-24T16:04:24.123456Z", 
  "attempt": 1,
  "max_attempts": 3,
  "delay_seconds": 1.0,
  "exception": "HTTP 503: Service temporarily unavailable"
}

{
  "event": "Retry succeeded",
  "level": "info",
  "timestamp": "2024-08-24T16:04:25.234567Z",
  "final_attempt": 2
}
```

## Retry Logic Details

### Exponential Backoff Schedule
- **Attempt 1**: Immediate
- **Attempt 2**: 1 second delay  
- **Attempt 3**: 2 seconds delay
- **Attempt 4**: 4 seconds delay (if max_attempts > 3)

### Retryable Conditions
- ✅ **5xx HTTP errors** (500, 502, 503, 504, etc.)
- ✅ **Connection timeouts**
- ✅ **Network connection errors**
- ❌ **4xx HTTP errors** (400, 401, 404, etc.) - Not retried
- ❌ **Invalid API keys** - Not retried
- ❌ **Malformed requests** - Not retried

### Performance Impact

| Scenario | Latency | Retry Overhead |
|----------|---------|----------------|
| Success (1st attempt) | ~300ms | 0ms |
| Success (2nd attempt) | ~1.3s | +1s delay |
| Success (3rd attempt) | ~3.3s | +3s delays |
| All attempts fail | ~7.3s | +7s delays |

## Testing

Run the test suite:
```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_retry.py -v
pytest tests/test_logging.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
d:\Downloads\ASSIGN\
├── main.py                 # Enhanced tweet generator
├── prompt_template.py      # Template system (from Q2)
├── retry_handler.py        # Exponential backoff logic
├── logging_config.py       # Structlog configuration
├── tests/
│   ├── test_retry.py      # Retry logic tests
│   └── test_logging.py    # Logging tests
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── requirements.txt      # Dependencies
├── tweet_generator.log   # Log file (created at runtime)
└── README.md             # This file
```

## Configuration Options

### Logging Configuration
```python
from logging_config import setup_logging

# Basic setup
setup_logging()

# Custom configuration  
setup_logging(
    log_level="DEBUG",      # DEBUG, INFO, WARNING, ERROR
    log_file="custom.log"   # Custom log file path
)
```

### Retry Configuration
```python
# In generate_tweet function
tweet = generate_tweet(
    topic="AI",
    tone="professional", 
    max_words=25,
    max_retries=5  # Custom retry count
)
```

## Error Handling Examples

### API Rate Limiting (429)
```json
{
  "event": "API request failed",
  "level": "error",
  "status_code": 429, 
  "error_message": "Rate limit exceeded",
  "retry_attempted": false
}
```

### Authentication Error (401)
```json
{
  "event": "API request failed", 
  "level": "error",
  "status_code": 401,
  "error_message": "Invalid API key",
  "retry_attempted": false
}
```

### Server Error with Successful Retry (503)
```json
{
  "event": "API request failed",
  "level": "error", 
  "status_code": 503
},
{
  "event": "Retry succeeded",
  "level": "info",
  "final_attempt": 2
}
```

## Security & Best Practices

- ✅ **No API keys in logs**: Sensitive data automatically filtered
- ✅ **Request/response truncation**: Large payloads truncated for readability
- ✅ **Structured logging**: Easy parsing and monitoring
- ✅ **Configurable verbosity**: Adjust logging detail as needed
- ✅ **File rotation ready**: Compatible with logrotate and similar tools

## Next Steps (Q4+)

- Database persistence for retry metrics
- Distributed tracing integration  
- Prometheus metrics export
- Circuit breaker pattern
- Async/await API calls
