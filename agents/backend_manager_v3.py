
from core.llm_backend import backend_planner_llm
from core.tool_executor import execute_tool as perform_action
from agents.end_turn_agent import EndTurnAgent
from datetime import datetime, timedelta
import json
import logging

class ContextV3:
    def __init__(self, user_query):
        self.user_query = user_query
        self.actions = []
        self.goal_state = None

    def update_with_action_result(self, action, result):
        self.actions.append((action, result))

    def actions_log(self):
        return str(self.actions)

    def last_action_result(self):
        if not self.actions:
            return ("None", "None")
        return self.actions[-1]

    def goal_satisfied(self):
        if not self.actions:
            return False
        last_action, last_result = self.actions[-1]
        if isinstance(last_result, str):
            if any(x in last_result.lower() for x in ["no matching events", "no emails", "i'm not sure", "error"]):
                return False
        return True

    def final_response(self):
        if not self.actions:
            return "I'm not sure what you wanted to do."
        last_action, last_result = self.actions[-1]
        return f"Based on the last action [{last_action}], here is what I found: {last_result}"

def extract_args_for_tool(tool_name, context, user_query):
    today = datetime.utcnow().date()
    if tool_name == "calendar_scan":
        end = today + timedelta(days=30)
        return {"start_date": today.strftime("%Y/%m/%d"), "end_date": end.strftime("%Y/%m/%d"), "query": user_query}
    if tool_name == "email_download_chunk":
        end = today
        start = end - timedelta(days=7)
        return {"start_date": start.strftime("%Y/%m/%d"), "end_date": end.strftime("%Y/%m/%d")}
    if tool_name == "meta_query":
        return {"query": user_query}
    return {}

def backend_manager_loop_v3(query, max_steps=10):
    end_turn_agent = EndTurnAgent()
    context = ContextV3(query)

    logging.info(f"FRONTEND -> BACKENDM: [User Query] {query}")

    for step in range(max_steps):
        if step == 0 or not context.goal_satisfied():
            last_action, last_result = context.last_action_result()

            if step == 0:
                planner_prompt = f"""
You are Riley2's Backend Manager LLM.
You must decide how to best fulfill the user's request.

Rules:
- If the user asks for factual information like the date or time, use get_current_time.
- If the user asks about calendar events, use calendar_scan.
- If the user asks about emails, use the email tools appropriately.
- If the user asks about your capabilities, use meta_query.
- If the user is making small talk, jokes, greetings, or general conversation, respond directly using LLM_ANSWER.

Examples:
User: "what day is it?"
→ {{"action": "get_current_time", "args": {{}}}}

User: "what's your name?"
→ {{"action": "LLM_ANSWER", "args": {{"response": "My name is Riley2, your helpful assistant!"}}}}

User: "scan my calendar for meetings next week"
→ {{"action": "calendar_scan", "args": {{"start_date": "2025/05/01", "end_date": "2025/05/07", "query": "meeting"}}}}

User: "download my last week's emails"
→ {{"action": "email_download_chunk", "args": {{}}}}

Available tools:
- calendar_scan(start_date, end_date, query)
- email_download_chunk(start_date, end_date)
- email_filter_by_sender(raw_emails, sender_email)
- email_summarize_batch(raw_emails)
- get_current_time()
- meta_query(query)

Respond STRICTLY in JSON:
{{"action": "<tool_name or LLM_ANSWER or META_QUERY or END_TURN>", "args": {{...}}}}
User Query: "{query}"
"""
            else:
                planner_prompt = f"""
You are Riley2's Backend Manager LLM.

Previous step result:
Tool used: {last_action}
Result: {last_result}

User's original request:
"{query}"

Reflect and decide next best step.

Respond in JSON:
{{"action": "<tool_name or META_QUERY or LLM_ANSWER or END_TURN or REQUEST_CLARIFICATION>", "args": {{...}}}}
"""

            planner_response = backend_planner_llm(planner_prompt)
            logging.info(f"BACKENDM RAW PLAN RESPONSE: {planner_response}")

            try:
                parsed = json.loads(planner_response)
            except Exception as e:
                logging.error(f"Planner LLM gave invalid JSON: {e}")
                repair_prompt = """
You failed to output valid JSON.
You must respond ONLY with valid JSON.

Example:
{{"action": "dummy_tool_search", "args": {{"query": "next meeting"}}}}

Retry the plan for: "{query}"
"""
                planner_response = backend_planner_llm(repair_prompt)
                try:
                    parsed = json.loads(planner_response)
                except Exception as e2:
                    logging.error(f"Planner retry failed again: {e2}")
                    return "I'm sorry, I could not understand the plan to fulfill your request."

            action = parsed.get("action")
            args = parsed.get("args", {})

            allowed_actions = [
                "calendar_scan", "email_download_chunk",
                "email_filter_by_sender", "email_summarize_batch",
                "get_current_time", "meta_query",
                "LLM_ANSWER", "END_TURN", "REQUEST_CLARIFICATION"
            ]
            if action not in allowed_actions:
                logging.error(f"Planner selected invalid action: {action}")
                feedback_prompt = """
The tool or agent you selected does not exist.

Example valid JSON:
{{"action": "calendar_scan", "args": {{"start_date": "2025/05/01", "end_date": "2025/06/01", "query": "trip"}}}}

Retry planning for original query: "{query}"
"""
                planner_response = backend_planner_llm(feedback_prompt)
                try:
                    parsed = json.loads(planner_response)
                except Exception as e3:
                    logging.error(f"Planner retry failed again: {e3}")
                    return "I'm sorry, the system could not find a valid way to fulfill your request."

                action = parsed.get("action")
                args = parsed.get("args", {})

            logging.info(f"BACKENDM LLM PLAN: {planner_response}")

            if action == "END_TURN":
                logging.info("BACKENDM: [End Turn Condition Met]")
                break

            if action == "LLM_ANSWER":
                final_response = args.get("response", "I'm not sure how to answer that.")
                logging.info(f"BACKENDM -> FRONTEND (LLM Direct): {final_response}")
                return final_response

            if action == "REQUEST_CLARIFICATION":
                question = args.get("question", "Can you clarify what you mean?")
                logging.info(f"BACKENDM -> FRONTEND (Clarification Request): {question}")
                return question

            result = perform_action(action, args)
            logging.info(f"BACKEND -> BACKENDM: [Action Result] {result}")
            context.update_with_action_result(action, result)

            if context.goal_satisfied():
                logging.info("BACKENDM: [Goal Satisfied]")
                break
        else:
            logging.info("BACKENDM: [Already satisfied, exiting loop]")
            break

    final_response = context.final_response()
    logging.info(f"BACKENDM -> FRONTEND: [Final Response] {final_response}")
    return final_response
