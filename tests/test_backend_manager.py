# PATCH for tests/test_backend_manager.py
# Purpose: Proper colorful logging for backend manager tests

import unittest
from core.llm_backend import BackendLLM
from core.logger_utils import log_agent_interaction, log_test_step, log_test_success

class TestBackendManager(unittest.TestCase):

    def setUp(self):
        self.backend_llm = BackendLLM()

    def test_choose_next_action_trip(self):
        log_test_step("Testing choose_next_action with 'trip to Italy'.")
        query = "Planning a trip to Italy"
        context = {}
        log_agent_interaction("BackendManager", "Planner", f"Received query: {query}")
        action = self.backend_llm.choose_next_action(query, context)
        log_agent_interaction("BackendManager", "Planner", f"Chosen action: {action}")
        self.assertEqual(action, "calendar_search")
        log_test_success("test_choose_next_action_trip")

    def test_choose_next_action_email(self):
        log_test_step("Testing choose_next_action with 'email from boss'.")
        query = "Check latest email from boss"
        context = {}
        log_agent_interaction("BackendManager", "Planner", f"Received query: {query}")
        action = self.backend_llm.choose_next_action(query, context)
        log_agent_interaction("BackendManager", "Planner", f"Chosen action: {action}")
        self.assertEqual(action, "email_search")
        log_test_success("test_choose_next_action_email")

    def test_get_decision(self):
        log_test_step("Testing get_decision end-turn logic.")
        prompt = "I have enough information now, thanks."
        log_agent_interaction("BackendManager", "DecisionLogic", f"Received prompt: {prompt}")
        decision = self.backend_llm.get_decision(prompt)
        log_agent_interaction("BackendManager", "DecisionLogic", f"Decision made: {decision}")
        self.assertEqual(decision, "yes")
        log_test_success("test_get_decision")

if __name__ == "__main__":
    unittest.main()