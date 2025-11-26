"""pytest configuration for opensearch-curator tests"""

import logging
import warnings
import sys


class SafeStreamHandler(logging.StreamHandler):
    """
    StreamHandler that silently ignores closed file errors during pytest teardown.

    Fixes: ValueError: I/O operation on closed file
    See: https://github.com/pytest-dev/pytest/issues/5502

    The issue occurs when:
    1. pytest closes log file handles during teardown
    2. OpenSearch/urllib3 client continues logging HTTP requests in threads
    3. Logging system tries to write to closed file handle
    """

    def emit(self, record):
        try:
            super().emit(record)
        except (ValueError, OSError):
            # Silently ignore closed file/OS errors during teardown
            pass

    def handleError(self, record):
        """Override to prevent logging.Handler.handleError from printing to stderr"""
        # Check if it's the expected closed file error
        exc_type, exc_value, _ = sys.exc_info()
        if exc_type is ValueError and 'closed file' in str(exc_value):
            # Silently ignore - this is expected during pytest teardown
            pass
        else:
            # For other errors, call the parent implementation
            super().handleError(record)


def pytest_configure(config):
    """Configure pytest with safe logging handlers for OpenSearch clients"""

    # Monkey-patch logging.Handler.handleError to suppress closed file errors
    original_handle_error = logging.Handler.handleError

    def safe_handle_error(self, record):
        """Suppress 'I/O operation on closed file' errors during pytest teardown"""
        exc_type, exc_value, _ = sys.exc_info()
        if exc_type is ValueError and 'closed file' in str(exc_value):
            # Silently ignore - expected during pytest teardown
            return
        # For other errors, use original behavior
        original_handle_error(self, record)

    logging.Handler.handleError = safe_handle_error

    # Replace handlers for all OpenSearch-related loggers
    for logger_name in ['opensearch', 'urllib3', 'opensearchpy', 'elastic_transport']:
        logger = logging.getLogger(logger_name)

        # Clear existing handlers
        logger.handlers.clear()

        # Add our safe handler
        safe_handler = SafeStreamHandler()
        safe_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)-9s %(name)22s %(funcName)22s:%(lineno)-4d %(message)s'
            )
        )
        logger.addHandler(safe_handler)

        # Don't propagate to avoid duplicate logs
        logger.propagate = False

    # Suppress OpenSearchWarning about system indices
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="opensearchpy"
    )
