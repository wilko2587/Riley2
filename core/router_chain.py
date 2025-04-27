from agents.backend_manager_v2 import backend_manager_loop_v2
from core.frontend_llm import frontend_llm_response

class Context:
    def __init__(self):
        self.actions = []

    def update_with_action_result(self, action, result):
        self.actions.append((action, result))

    def actions_log(self):
        return str(self.actions)

    def last_action_result(self):
        if not self.actions:
            return ("None", "None")
        return self.actions[-1]

    def final_response(self):
        if not self.actions:
            return "I'm not sure what you wanted to do."
        last_action, last_result = self.actions[-1]
        return f"Based on the last action [{last_action}], here is what I found: {last_result}"

def classify_query(query):
    social_keywords = [
        "hi", "hello", "how are you", "joke", "tell me", "chat",
        "conversation", "what can you do", "what controls", "what tools", "how can you help"
    ]
    lowered = query.lower()
    if any(word in lowered for word in social_keywords):
        return "chat"
    return "work"

def route_user_query(user_query):
    context = Context()

    classification = classify_query(user_query)

    if classification == "chat":
        return frontend_llm_response(user_query)
    else:
        return backend_manager_loop_v2(user_query, context)