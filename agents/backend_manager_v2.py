from core.llm_backend import backend_planner_llm
from core.tool_executor import execute_tool as perform_action
from agents.end_turn_agent import EndTurnAgent
from datetime import datetime, timedelta
import json
import logging

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

def backend_manager_loop_v2(query, context, max_steps=8):
    end_turn_agent = EndTurnAgent()

    logging.info(f"FRONTEND -> BACKENDM: [User Query] {query}")

    for step in range(max_steps):
        if step == 0:
            planner_prompt = f"""
You are Riley2's Backend Manager LLM.
Your job is to solve the user's request by either:

- Selecting an appropriate backend tool
- Or using the Meta Agent to explain system capabilities
- Or directly responding via LLM natural text

Available tools:
- calendar_scan(start_date, end_date, query)
- email_download_chunk(start_date, end_date)
- email_filter_by_sender(raw_emails, sender_email)
- email_summarize_batch(raw_emails)
- get_current_time()
- meta_query(query)

You may directly answer using "LLM_ANSWER" if no tool needed.

Respond STRICTLY in JSON:
{{ 
  "action": "<tool_name or META_QUERY or LLM_ANSWER or END_TURN>", 
  "args": {{ ... }}
}}
"""
        else:
            last_action, last_result = context.last_action_result()
            planner_prompt = f"""
You are Riley2's Backend Manager LLM.

You just attempted:
Tool: {last_action}
Result: {last_result}

User's original goal: "{query}"

Think:
- Retry broader search?
- Different tool?
- Clarify with user?
- Use Meta Agent?
- End turn if complete?

Respond STRICTLY in JSON:
{{ 
  "action": "<tool_name or META_QUERY or REQUEST_CLARIFICATION or LLM_ANSWER or END_TURN>", 
  "args": {{ ... }}
}}
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

        if action == "REQUEST_CLARIFICATION":
            question = args.get("question", "Can you clarify what you mean?")
            logging.info(f"BACKENDM -> FRONTEND (Clarification Request): {question}")
            return question

        result = perform_action(action, args)
        logging.info(f"BACKEND -> BACKENDM: [Action Result] {result}")

        context.update_with_action_result(action, result)

        if end_turn_agent.should_end_turn(query, context):
            logging.info("BACKENDM: [End Turn Condition Met]")
            break

    final_response = context.final_response()
    logging.info(f"BACKENDM -> FRONTEND: [Final Response] {final_response}")

    return final_response