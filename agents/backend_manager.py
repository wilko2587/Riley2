
from core.llm_backend import backend_planner_llm
from core.tool_executor import execute_tool as perform_action
from agents.end_turn_agent import EndTurnAgent
from datetime import datetime, timedelta
import json
import logging

def extract_args_for_tool(tool_name, context, user_query):
    if tool_name == "calendar_search":
        return {"query": user_query}
    if tool_name == "email_download_chunk":
        end = datetime.utcnow().date()
        start = end - timedelta(days=7)
        return {"start_date": start.strftime("%Y/%m/%d"), "end_date": end.strftime("%Y/%m/%d")}
    return {}

def backend_manager_loop(query, context, max_steps=5):
    end_turn_agent = EndTurnAgent()

    logging.info(f"FRONTEND -> BACKENDM: [User Query] {query}")

    for step in range(max_steps):
        planner_prompt = f"""
You are Riley2's Backend Manager LLM.
You are responsible for deciding which backend tool to execute next based on:

- User Query: {query}
- Past Actions and Results: {context.actions_log()}

Available tools:
- calendar_search(query)
- email_download_chunk(start_date, end_date)
- email_filter_by_sender(raw_emails, sender_email)
- email_summarize_batch(raw_emails)
- get_current_time()

You may also directly respond using natural language by selecting "action": "LLM_ANSWER" if no tool is appropriate.

Respond ONLY in strict JSON:
{{ 
  "action": "<tool_name or LLM_ANSWER or END_TURN>", 
  "args": {{ ... }}
}}

THINK step-by-step before deciding.
"""

        planner_response = backend_planner_llm(planner_prompt)
        logging.info(f"BACKENDM LLM PLAN: {planner_response}")

        try:
            parsed = json.loads(planner_response)
        except Exception as e:
            logging.error(f"Failed to parse planner response: {e}")
            break

        action = parsed.get("action")
        args = parsed.get("args", {})

        if action == "END_TURN":
            logging.info("BACKENDM: [End Turn Condition Met]")
            break

        if action == "LLM_ANSWER":
            final_response = args.get("response", "I'm not sure how to answer that.")
            logging.info(f"BACKENDM -> FRONTEND (LLM Direct): {final_response}")
            return final_response

        result = perform_action(action, args)
        logging.info(f"BACKEND -> BACKENDM: [Action Result] {result}")

        context.update_with_action_result(action, result)

        if end_turn_agent.should_end_turn(query, context):
            logging.info("BACKENDM: [End Turn Condition Met (Agent Decision)]")
            break

    final_response = context.final_response()
    logging.info(f"BACKENDM -> FRONTEND: [Final Response] {final_response}")

    return final_response
