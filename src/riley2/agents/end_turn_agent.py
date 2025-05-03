from riley2.core.llm_backend import backend_llm

class EndTurnAgent:
    def should_end_turn(self, query, context):
        prompt = f"""
        User asked: {query}
        Progress so far: {context.actions_log()}
        Do we have enough information to answer the user's query? Answer with "yes" or "no" only.
        """
        decision = backend_llm.get_decision(prompt)
        return decision.lower().strip() == "yes"