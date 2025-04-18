from agents.explorer_agent import handle_explorer_task
from agents.calendar_agent import handle_calendar_task
from agents.email_agent import handle_email_task

def handle_user_input(user_input):
    # Very basic routing logic for now
    if "calendar" in user_input.lower():
        return handle_calendar_task(user_input)
    elif "email" in user_input.lower():
        return handle_email_task(user_input)
    elif any(cmd in user_input.lower() for cmd in ["cd", "ls", "pwd", "explore", "directory"]):
        return handle_explorer_task(user_input)
    else:
        return "Sorry, I’m not sure how to handle that yet."
