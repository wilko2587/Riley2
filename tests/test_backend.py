
import pytest

@pytest.fixture(scope="session")
def verbose_flag(request):
    return request.config.getoption("verbose") >= 3
import pytest
# PATCH for tests/test_backend.py
# Purpose: Inject proper colorful, agent-tagged logging during tests

import unittest
from riley2.core.llm_backend import summarize_text, interpret_tool_command, backend_planner_llm
from riley2.core.logger_utils import log_agent_interaction, log_test_step, log_test_success

class TestBackend(unittest.TestCase):

    def test_summarize_text_basic(self):
        log_test_step("Testing summarize_text basic functionality.")
        input_text = "Meeting tomorrow at 9 AM with sales team."
        log_agent_interaction("BackendManager", "Summarizer", f"Input to summarize: {input_text}")
        result = summarize_text(input_text, verbose=verbose_flag)
        log_agent_interaction("BackendManager", "Summarizer", f"Summarized result: {result}")
        self.assertIn("meeting", result.lower())
        log_test_success("test_summarize_text_basic")

    def test_interpret_tool_command_basic(self):
        log_test_step("Testing interpret_tool_command basic functionality.")
        tool = "calendar_search"
        args = {"date": "2025-05-15"}
        output = "Meeting scheduled for 9 AM with Sales."
        log_agent_interaction("BackendManager", "ToolInterpreter", f"Tool: {tool}, Args: {args}, Output: {output}")
        human_response = interpret_tool_command(tool, args, output)
        log_agent_interaction("BackendManager", "ToolInterpreter", f"Human-readable output: {human_response}")
        self.assertIn("meeting", human_response.lower())
        log_test_success("test_interpret_tool_command_basic")

    def test_backend_planner_llm(self):
        log_test_step("Testing backend_planner_llm decision-making.")
        prompt = "What events are coming up next week?"
        log_agent_interaction("BackendPlanner", "Planner", f"Planning with prompt: {prompt}")
        plan = backend_planner_llm(prompt)
        log_agent_interaction("BackendPlanner", "Planner", f"Planner decided: {plan}")
        self.assertIsInstance(plan, str)
        log_test_success("test_backend_planner_llm")

if __name__ == "__main__":
    unittest.main()
