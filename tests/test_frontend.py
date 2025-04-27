import inspect
from test_logger import setup_test_logger

test_logger = setup_test_logger()

def test_frontend_dummy():
    current_function = inspect.currentframe().f_code.co_name
    test_logger.info(f"\033[93m💠 === Starting Test: {current_function} ===\033[0m")
    test_logger.info('Starting test_frontend_dummy')

    dummy_input = "What meetings do I have today?"
    dummy_response = "You have a meeting at 3 PM today with the marketing team."
    assert isinstance(dummy_response, str) and "meeting" in dummy_response.lower(), "Response should mention 'meeting'."

    test_logger.info(f"\033[92m✅ === Finished Test: {current_function} ===\033[0m")
    test_logger.info('')
