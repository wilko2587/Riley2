# Clean and correct version of tests/test_calendar_trip_to_italy.py

import unittest
from core.llm_backend import summarize_text, interpret_tool_command
from core.logger_utils import log_agent_interaction, log_test_step, log_test_success

class TestCalendarTripToItaly(unittest.TestCase):

    def test_trip_to_italy_flow(self):
        log_test_step("Simulating planning a trip to Italy.")

        # Step 1: User asks about planning a trip
        user_query = "I'm planning a trip to Italy next month."
        log_agent_interaction("FrontendAgent", "UserInput", f"User query: {user_query}")

        # Step 2: Backend suggests looking up the calendar
        action = "calendar_search"
        args = {"location": "Italy", "date_range": "next month"}
        backend_response = "Found a 10-day window free in June for travel."

        log_agent_interaction("BackendManager", "Planner", f"Suggested action: {action}")
        log_agent_interaction("BackendManager", "ToolExecutor", f"Executed calendar search with args: {args}")

        # Step 3: Interpret backend response
        human_readable = interpret_tool_command(action, args, backend_response)
        log_agent_interaction("BackendManager", "ToolInterpreter", f"Interpreted tool output: {human_readable}")

        # Step 4: Summarize for the user
        summary = summarize_text(human_readable)
        log_agent_interaction("FrontendAgent", "Summarizer", f"Summary for user: {summary}")

        # Assert basic expected flow
        self.assertIn("Italy", human_readable)
        self.assertIn("travel", summary.lower())

        log_test_success("test_trip_to_italy_flow")

if __name__ == "__main__":
    unittest.main()