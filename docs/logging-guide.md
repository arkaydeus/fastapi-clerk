# Custom Logging Guide

This project uses a custom JSON-structured logging system that extends Python's standard logging. This guide explains how to properly use it in your code.

## Logging Methods

There are two ways to use the logging system:

### 1. Direct Logger Methods with `extra` Parameter (Recommended)

```python
from app.core.logging import logger

# Example with context data
logger.info("User logged in", extra={"props": {"user_id": "123", "ip": "127.0.0.1"}})

# Example with exception info
try:
    # some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.error("Division error", extra={"props": {"value": 0}}, exc_info=e)

# Simple logging without context
logger.debug("Application started")
```

### 2. Custom Helper Functions

The logging module provides convenience methods that handle the `props` parameter for you:

```python
from app.core.logging import info, error, debug, warning, critical

# These functions automatically handle the props structure
info("User logged in", context={"user_id": "123", "ip": "127.0.0.1"})

try:
    # some code that might raise an exception
    result = 1 / 0
except Exception as e:
    error("Division error", context={"value": 0}, exc_info=e)

# Simple logging without context
debug("Application started")
```

## Common Mistake to Avoid

**Do not use** the `context` parameter directly with the standard logger methods:

```python
# ❌ INCORRECT - Will raise TypeError
logger.info("Message", context={"key": "value"})  # TypeError: Logger._log() got an unexpected keyword argument 'context'

# ✅ CORRECT - Use extra with props instead
logger.info("Message", extra={"props": {"key": "value"}})

# ✅ CORRECT - Or use the helper functions
info("Message", context={"key": "value"})
```

## Log Levels

The application uses the following log levels:

- `DEBUG`: Detailed information, typically for development
- `INFO`: Confirmation that things are working as expected
- `WARNING`: Something unexpected happened but the app continues running
- `ERROR`: A more serious issue that prevented a function from working
- `CRITICAL`: A serious error that may prevent the app from continuing

## JSON Output Format

All logs are formatted as JSON with the following structure:

```json
{
  "timestamp": "2023-05-01T12:34:56.789Z",
  "level": "INFO",
  "message": "User logged in",
  "module": "auth",
  "function": "authenticate_user",
  "line": 42,
  "user_id": "123",
  "ip": "127.0.0.1"
}
```

This structured format makes logs easier to parse and analyze with tools like ELK Stack or CloudWatch Logs.

## Environment-Based Log Levels

- In `development` mode: `DEBUG` and above are logged
- In `production` mode: `INFO` and above are logged

The environment is controlled by the `API_ENV` environment variable.
