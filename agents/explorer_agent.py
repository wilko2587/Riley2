from core.system_interface import run_command

def handle_explorer_task(task):
    # Example logic
    if "pwd" in task:
        return run_command("cd")
    elif "ls" in task:
        return run_command("dir")
    elif "cd" in task:
        return "Changing directories isn't yet implemented."
    else:
        return "ExplorerAgent couldn't understand your command."
