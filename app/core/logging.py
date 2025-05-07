import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            str: JSON formatted log string
        """
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra contextual information if available
        if hasattr(record, "props"):
            log_record.update(record.props)

        return json.dumps(log_record)


def get_logger(name: str = "app") -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Name for the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)

    # Don't propagate to root logger
    logger.propagate = False

    # Clear existing handlers to avoid duplicates on reloads
    if logger.handlers:
        logger.handlers.clear()

    # Set log level based on environment
    log_level = logging.DEBUG if settings.api_env == "development" else logging.INFO
    logger.setLevel(log_level)

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    return logger


# Create a default logger instance
logger = get_logger("app")


def log_with_context(
    level: int,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Exception] = None,
) -> None:
    """
    Log a message with additional context.

    Args:
        level: Logging level (e.g., logging.INFO)
        message: Log message
        context: Additional context to include in the log
        exc_info: Exception information
    """
    extra = {"props": context or {}}
    logger.log(level, message, extra=extra, exc_info=exc_info)


# Convenience methods
def debug(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Log a debug message with optional context."""
    log_with_context(logging.DEBUG, message, context)


def info(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an info message with optional context."""
    log_with_context(logging.INFO, message, context)


def warning(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Exception] = None,
) -> None:
    """Log a warning message with optional context and exception info."""
    log_with_context(logging.WARNING, message, context, exc_info)


def error(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Exception] = None,
) -> None:
    """Log an error message with optional context and exception info."""
    log_with_context(logging.ERROR, message, context, exc_info)


def critical(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    exc_info: Optional[Exception] = None,
) -> None:
    """Log a critical message with optional context and exception info."""
    log_with_context(logging.CRITICAL, message, context, exc_info)
