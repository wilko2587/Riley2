import pytest
import inspect
from src.riley2.core.logger_utils import (
    log_test_step,
    log_test_success,
    log_llm_call,
    log_test_failure,
    show_event_sequence,
    log_component_interaction,
    test_logger
)

@pytest.fixture(scope="session")
def verbose_flag(request):
    return request.config.getoption("verbose") >= 3

def test_frontend_dummy():
    current_function = inspect.currentframe().f_code.co_name
    test_logger.info(f"=== Starting Test: {current_function} ===")
    
    # Use our enhanced logging
    log_test_step("Testing frontend response to meeting query")
    
    # Simulate a user query
    dummy_input = "What meetings do I have today?"
    
    # Log component interaction
    log_component_interaction("USER", "FRONTEND", dummy_input)
    
    # Simulate an LLM call
    mock_prompt = "User is asking about meetings today. Generate a helpful response."
    mock_response = "You have a meeting at 3 PM today with the marketing team."
    log_llm_call("Frontend LLM", mock_prompt, mock_response)
    
    # Log the frontend's response back to the user
    log_component_interaction("FRONTEND", "USER", mock_response, direction="<<<")
    
    # Show the sequence of events
    show_event_sequence("Frontend Query Flow", [
        {"type": "Input", "source": "User", "target": "Frontend", "description": "Asked about meetings"},
        {"type": "Process", "source": "Frontend", "target": "LLM", "description": "Generated query response"},
        {"type": "Output", "source": "Frontend", "target": "User", "description": "Provided meeting information"}
    ])
    
    # Run the assertion
    try:
        assert isinstance(mock_response, str) and "meeting" in mock_response.lower(), "Response should mention 'meeting'."
        log_test_success(current_function)
    except AssertionError as e:
        log_test_failure(current_function, str(e))
        raise
        
    test_logger.info(f"=== Finished Test: {current_function} ===")
