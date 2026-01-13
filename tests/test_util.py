import logging
import sys
import pytest
from src.fhir_sheets.util.CustomLoggingFormatter import CustomLoggingFormatter


class TestCustomLoggingFormatter:
    def test_format_basic(self):
        formatter = CustomLoggingFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert "Test message" in formatted
        assert "INFO" in formatted or "test" in formatted  # Depending on formatter style

    def test_format_with_exception(self):
        formatter = CustomLoggingFormatter()
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        formatted = formatter.format(record)
        assert "Error occurred" in formatted
        assert "ValueError" in formatted or "Test error" in formatted
