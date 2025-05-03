"""
Global pytest configuration for Riley2 tests.
This file sets up enhanced colorful logging for all test runs.
"""

import pytest
import logging
import os
import sys
import atexit
from datetime import datetime

# Import our enhanced logging utils
from src.riley2.core.logger_utils import (
    test_logger,
    logger,  # Also import the main logger
    ColoredFormatter,
    HttpcoreFilter,
    log_system_event,
    SECTION_BORDER
)

# Global file handler reference to prevent premature closing
_file_handler = None
_console_handler = None

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Set up colored logging for all tests automatically."""
    global _file_handler, _console_handler
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Clear and configure the test log file with maximum verbosity
    log_file = os.path.join('logs', 'riley2_test.log')
    
    # Remove any existing file handlers from test_logger
    for handler in list(test_logger.handlers):
        if isinstance(handler, logging.FileHandler):
            test_logger.removeHandler(handler)
    
    # Create a new file handler with maximum verbosity
    _file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    # Add it to both loggers
    test_logger.setLevel(logging.DEBUG)
    test_logger.addHandler(_file_handler)
    
    # Also add it to the main logger to capture everything
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_file_handler)
    
    # Add console handler for standard output
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setLevel(logging.INFO)
    _console_handler.setFormatter(ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _console_handler.addFilter(HttpcoreFilter())
    
    # Add console handler to both loggers
    test_logger.addHandler(_console_handler)
    
    # Add timestamp to start of test session
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_system_event("TEST_SESSION", f"Starting test session at {timestamp} with enhanced colorful logging (MAXIMUM VERBOSITY)")
    test_logger.debug("Debug logging enabled - capturing detailed test information")
    
    yield
    
    # Log system shutdown with stats - but don't flush or close handlers yet
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        log_system_event("TEST_SESSION", f"Test session complete at {timestamp}")
    except:
        pass  # Ignore errors during shutdown

@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """Custom pytest configuration."""
    # Register a custom marker for tests requiring mocks
    config.addinivalue_line("markers", "requires_mocks: mark test as requiring mock objects")
    
    # Register a marker for integration tests
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    
    # Disable output capture to ensure all messages are logged
    config.option.capture = "no"

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Called before each test is run."""
    # Get test name for better logging
    test_name = item.name
    # Log the start of the test with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        test_logger.info(f"=== Starting Test: {test_name} ===")
        test_logger.debug(f"Test setup started at {timestamp}")
        
        # Log any test markers for better debugging
        for marker in item.iter_markers():
            test_logger.debug(f"Test marker: {marker.name}")
    except Exception:
        # If logging fails, continue with the test
        pass

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    """Called after each test is run."""
    # Get test name for better logging
    test_name = item.name
    # Log the end of the test
    try:
        test_logger.info(f"=== Finished Test: {test_name} ===")
        test_logger.debug(f"Test teardown completed")
    except Exception:
        # If logging fails, continue with the test cleanup
        pass

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Called to create a test report for each phase of a test's execution."""
    outcome = yield
    report = outcome.get_result()
    
    # Log additional information about test execution phases
    if report.when == "call":  # Only log after the test function has been called
        try:
            if report.passed:
                test_logger.debug(f"Test '{item.name}' PASSED - Duration: {report.duration:.4f}s")
            elif report.failed:
                test_logger.error(f"Test '{item.name}' FAILED - Duration: {report.duration:.4f}s")
                if hasattr(report, "longrepr"):
                    test_logger.debug(f"Failure details:\n{report.longreprtext}")
            elif report.skipped:
                test_logger.info(f"Test '{item.name}' SKIPPED - Reason: {report.longrepr[2]}")
        except Exception:
            # If logging fails, continue
            pass

# Use a simplified version that doesn't try to access handlers directly
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    try:
        print(f"Test session finished with exit status: {exitstatus}")
        print(f"Total tests collected: {getattr(session, 'testscollected', 0)}")
        print(f"Tests failed: {getattr(session, 'testsfailed', 0)}")
    except Exception:
        pass