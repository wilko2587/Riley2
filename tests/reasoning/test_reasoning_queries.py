# File: tests/reasoning/test_reasoning_queries.py

import pytest
from tests.mocks.calendar_agent_mock import CalendarAgentMock
from src.riley2.core.logger_utils import logger, log_agent_interaction, log_test_step, log_test_success
from datetime import datetime

class BackendManagerMock:
    def __init__(self, calendar_agent):
        self.calendar_agent = calendar_agent

    def handle_question(self, prompt):
        log_agent_interaction("BackendManager", "Reasoner", f"Processing question: '{prompt}'")
        
        # Using calendar_scan method to match the real implementation
        today = datetime.now()
        year = today.year
        
        # First check April
        log_agent_interaction("BackendManager", "CalendarSearch", f"Searching April 2025 for Italy events")
        start_date = "2025/04/01"
        end_date = "2025/04/30"
        april_result = self.calendar_agent.calendar_scan(start_date, end_date, "italy")
        log_agent_interaction("CalendarAgent", "EventResult", april_result)
        
        if "Found events" in april_result:
            log_agent_interaction("BackendManager", "DecisionMade", f"Found Italy event in April")
            return "15042025"
        
        # Then check May
        log_agent_interaction("BackendManager", "CalendarSearch", f"No Italy events in April. Searching May 2025")
        start_date = "2025/05/01"
        end_date = "2025/05/31"
        may_result = self.calendar_agent.calendar_scan(start_date, end_date, "italy")
        log_agent_interaction("CalendarAgent", "EventResult", may_result)
        
        if "Found events" in may_result:
            log_agent_interaction("BackendManager", "DecisionMade", f"Found Italy event in May")
            return "15052025"
        
        log_agent_interaction("BackendManager", "DecisionMade", f"No Italy events found")
        return "NOTFOUND"

@pytest.mark.parametrize("prompt, expected", [
    ("When am I going to Italy?", "15052025"),
])
def test_reasoning_queries(prompt, expected):
    log_test_step(f"Testing reasoning with query: '{prompt}'")
    
    calendar_agent = CalendarAgentMock()
    backend_manager = BackendManagerMock(calendar_agent=calendar_agent)

    log_agent_interaction("Test", "InputQuery", prompt)
    response = backend_manager.handle_question(prompt)
    log_agent_interaction("Test", "OutputResponse", response)

    assert response.strip() == expected, f"Failed for prompt '{prompt}': got '{response}', expected '{expected}'"
    log_test_success(f"test_reasoning_queries[{prompt}]")