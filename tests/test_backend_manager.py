import pytest

@pytest.fixture(scope="session")
def verbose_flag(request):
    return request.config.getoption("verbose") >= 3

import unittest
import json
from src.riley2.core.llm_backend import BackendLLM
from src.riley2.core.logger_utils import (
    log_agent_interaction,
    log_test_step,
    log_test_success,
    log_test_failure,
    log_decision_point,
    log_llm_call,
    log_tool_usage,
    log_component_interaction,
    show_event_sequence,
    test_logger,
    SECTION_BORDER
)

class TestBackendManager(unittest.TestCase):

    def setUp(self):
        self.backend_llm = BackendLLM()
        test_logger.info(f"{SECTION_BORDER}")
        test_logger.info("Setting up BackendManager test")
        test_logger.info(f"{SECTION_BORDER}")

    def test_choose_next_action_trip(self):
        current_function = "test_choose_next_action_trip"
        test_logger.info(f"=== Starting Test: {current_function} ===")
        
        log_test_step("Testing BackendManager's decision-making for a trip to Italy query")
        
        # Simulate user query
        query = "Planning a trip to Italy"
        context = {}
        
        # Log the process with color and structure
        log_component_interaction("USER", "BACKEND_MANAGER", query)
        
        # Log the LLM reasoning process (simulated)
        mock_prompt = f"Based on the query '{query}', decide which action to take. Options: calendar_search, email_search, knowledge_lookup"
        mock_reasoning = """
        The query is about planning a trip to Italy, which is a future event. 
        This is most likely related to scheduling or checking existing plans.
        The calendar_search tool would be most appropriate to find any existing
        trip details or to help plan a new trip by checking availability.
        """
        log_llm_call("BackendLLM", mock_prompt, mock_reasoning, {"temperature": 0.2})
        
        # Log the decision point with options
        options = ["calendar_search", "email_search", "knowledge_lookup"]
        action = self.backend_llm.choose_next_action(query, context)
        log_decision_point("BackendManager", options, action, "Trip to Italy requires calendar search to check schedules")
        
        # Simulate the tool execution
        mock_calendar_args = {"query": "trip to Italy", "start_date": "2025-05-01", "end_date": "2025-06-30"}
        mock_result = {"events": [{"title": "Italy Trip", "date": "2025-05-15", "duration": "14 days"}]}
        log_tool_usage("calendar_search", mock_calendar_args, json.dumps(mock_result))
        
        # Log the response back to the user
        response = "I found your Italy Trip scheduled for May 15th, 2025 for a duration of 14 days."
        log_component_interaction("BACKEND_MANAGER", "USER", response, direction="<<<")
        
        # Show the complete flow of events
        show_event_sequence("Italy Trip Query Flow", [
            {"type": "Input", "source": "User", "target": "BackendManager", "description": "Asked about trip to Italy"},
            {"type": "Decision", "source": "BackendManager", "target": "LLM", "description": "Determined calendar search needed"},
            {"type": "Action", "source": "BackendManager", "target": "CalendarAgent", "description": "Executed calendar search"},
            {"type": "Result", "source": "CalendarAgent", "target": "BackendManager", "description": "Found Italy trip on May 15th"},
            {"type": "Output", "source": "BackendManager", "target": "User", "description": "Provided trip details"}
        ])
        
        # Run the assertion
        try:
            self.assertEqual(action, "calendar_search")
            log_test_success(current_function)
        except AssertionError as e:
            log_test_failure(current_function, str(e))
            raise
            
        test_logger.info(f"=== Finished Test: {current_function} ===")

    def test_choose_next_action_email(self):
        current_function = "test_choose_next_action_email"
        test_logger.info(f"=== Starting Test: {current_function} ===")
        
        log_test_step("Testing BackendManager's decision-making for email search query")
        
        # Simulate user query
        query = "Check latest email from boss"
        context = {}
        
        # Log component interaction
        log_component_interaction("USER", "BACKEND_MANAGER", query)
        
        # Log LLM reasoning (simulated)
        mock_prompt = f"Based on the query '{query}', decide which action to take. Options: calendar_search, email_search, knowledge_lookup"
        mock_reasoning = """
        The query is explicitly asking about emails, specifically the latest email from the boss.
        This is clearly related to email communication rather than scheduling or knowledge lookup.
        The email_search tool is the most appropriate choice to find recent emails from a specific sender.
        """
        log_llm_call("BackendLLM", mock_prompt, mock_reasoning, {"temperature": 0.2})
        
        # Log decision point
        options = ["calendar_search", "email_search", "knowledge_lookup"]
        action = self.backend_llm.choose_next_action(query, context)
        log_decision_point("BackendManager", options, action, "Query about email from boss requires email_search")
        
        # Simulate tool execution
        mock_email_args = {"sender": "boss@company.com", "limit": 1}
        mock_result = {"emails": [{"subject": "Project Update", "date": "2025-05-02", "snippet": "Please provide status on Riley2..."}]}
        log_tool_usage("email_search", mock_email_args, json.dumps(mock_result))
        
        # Log response
        response = "The latest email from your boss is from today with the subject 'Project Update'. It starts with: 'Please provide status on Riley2...'"
        log_component_interaction("BACKEND_MANAGER", "USER", response, direction="<<<")
        
        # Show event sequence
        show_event_sequence("Email Query Flow", [
            {"type": "Input", "source": "User", "target": "BackendManager", "description": "Asked about latest boss email"},
            {"type": "Decision", "source": "BackendManager", "target": "LLM", "description": "Determined email search needed"},
            {"type": "Action", "source": "BackendManager", "target": "EmailAgent", "description": "Executed email search"},
            {"type": "Result", "source": "EmailAgent", "target": "BackendManager", "description": "Found latest email about Project Update"},
            {"type": "Output", "source": "BackendManager", "target": "User", "description": "Provided email details"}
        ])
        
        # Run assertion
        try:
            self.assertEqual(action, "email_search")
            log_test_success(current_function)
        except AssertionError as e:
            log_test_failure(current_function, str(e))
            raise
            
        test_logger.info(f"=== Finished Test: {current_function} ===")

    def test_get_decision(self):
        current_function = "test_get_decision"
        test_logger.info(f"=== Starting Test: {current_function} ===")
        
        log_test_step("Testing BackendManager's end-turn decision logic")
        
        # Simulate prompt
        prompt = "I have enough information now, thanks."
        
        # Log interaction
        log_component_interaction("USER", "BACKEND_MANAGER", prompt)
        
        # Log LLM reasoning
        mock_prompt = f"Based on user message '{prompt}', should we end the conversation? (yes/no)"
        mock_reasoning = """
        The user has explicitly stated they have enough information.
        They've used a clear ending phrase "thanks" which typically signals conversation closure.
        There's no question or request for additional information.
        Therefore, it's appropriate to end the conversation turn.
        """
        log_llm_call("BackendLLM", mock_prompt, mock_reasoning, {"temperature": 0.1})
        
        # Get decision
        decision = self.backend_llm.get_decision(prompt)
        
        # Log decision
        log_decision_point("BackendManager", ["continue", "end conversation"], 
                          "end conversation" if decision == "yes" else "continue",
                          "User indicated they have enough information")
        
        # Show event sequence
        show_event_sequence("End Turn Decision Flow", [
            {"type": "Input", "source": "User", "target": "BackendManager", "description": "Said they have enough information"},
            {"type": "Analysis", "source": "BackendManager", "target": "LLM", "description": "Analyzed if conversation should end"},
            {"type": "Decision", "source": "BackendManager", "target": "System", "description": "Decided to end the conversation turn"}
        ])
        
        # Run assertion
        try:
            self.assertEqual(decision, "yes")
            log_test_success(current_function)
        except AssertionError as e:
            log_test_failure(current_function, str(e))
            raise
            
        test_logger.info(f"=== Finished Test: {current_function} ===")

if __name__ == "__main__":
    unittest.main()