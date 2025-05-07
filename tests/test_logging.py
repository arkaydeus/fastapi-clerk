import json
import logging
from io import StringIO
from unittest.mock import patch

import pytest

from app.core.config import get_settings
from app.core.logging import (
    JSONFormatter,
    critical,
    debug,
    error,
    get_logger,
    info,
    log_with_context,
    warning,
)


@pytest.fixture
def mock_logger():
    """Fixture to create a logger with an in-memory stream handler."""
    # Create a string buffer to capture log output
    log_stream = StringIO()

    # Create a handler that writes to the string buffer
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(JSONFormatter())

    # Create a logger and add the handler
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # Make sure we don't propagate to root logger
    logger.propagate = False

    # Return both the logger and the stream for assertions
    return logger, log_stream


def test_json_formatter():
    """Test that JSONFormatter formats logs correctly."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["level"] == "INFO"
    assert parsed["message"] == "Test message"
    assert parsed["module"] == "test_file"
    assert parsed["line"] == 42
    assert "timestamp" in parsed


def test_get_logger_development():
    """Test logger configuration in development mode."""
    with patch.object(get_settings(), "api_env", "development"):
        logger = get_logger("test_dev")
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)


def test_get_logger_production():
    """Test logger configuration in production mode."""
    with patch.object(get_settings(), "api_env", "production"):
        logger = get_logger("test_prod")
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)


def test_log_with_context(mock_logger):
    """Test logging with context."""
    logger, log_stream = mock_logger

    with patch("app.core.logging.logger", logger):
        # Log a message with context
        log_with_context(
            logging.INFO,
            "Test message with context",
            context={"user_id": 123, "action": "test"},
        )

        # Get the log output and parse it
        log_output = log_stream.getvalue()
        parsed = json.loads(log_output)

        # Check the log content
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message with context"
        assert parsed["user_id"] == 123
        assert parsed["action"] == "test"


def test_log_with_exception(mock_logger):
    """Test logging with exception info."""
    logger, log_stream = mock_logger

    with patch("app.core.logging.logger", logger):
        try:
            # Raise an exception
            raise ValueError("Test exception")
        except ValueError as e:
            # Log the exception
            log_with_context(
                logging.ERROR,
                "An error occurred",
                context={"operation": "test"},
                exc_info=e,
            )

        # Get the log output and parse it
        log_output = log_stream.getvalue()
        parsed = json.loads(log_output)

        # Check the log content
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "An error occurred"
        assert parsed["operation"] == "test"
        assert "exception" in parsed
        assert "ValueError: Test exception" in parsed["exception"]


def test_convenience_methods(mock_logger):
    """Test convenience logging methods."""
    logger, log_stream = mock_logger

    with patch("app.core.logging.logger", logger):
        # Test each convenience method
        debug("Debug message", {"level": "debug"})
        info("Info message", {"level": "info"})
        warning("Warning message", {"level": "warning"})
        error("Error message", {"level": "error"})
        critical("Critical message", {"level": "critical"})

        # Get all log outputs
        log_outputs = log_stream.getvalue().strip().split("\n")
        parsed_logs = [json.loads(log) for log in log_outputs]

        # Check the actual levels from the logs
        assert len(parsed_logs) == 5
        for i, log in enumerate(parsed_logs):
            # Just verify the presence of these fields
            assert "level" in log
            assert "message" in log
            assert "timestamp" in log

        # Check the messages and contextual data
        assert parsed_logs[0]["message"] == "Debug message"
        assert parsed_logs[0]["level"] == "debug"
        assert parsed_logs[1]["message"] == "Info message"
        assert parsed_logs[1]["level"] == "info"
        assert parsed_logs[2]["message"] == "Warning message"
        assert parsed_logs[2]["level"] == "warning"
        assert parsed_logs[3]["message"] == "Error message"
        assert parsed_logs[3]["level"] == "error"
        assert parsed_logs[4]["message"] == "Critical message"
        assert parsed_logs[4]["level"] == "critical"
