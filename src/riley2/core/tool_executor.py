from riley2.core.tool_registry import TOOL_FUNCTIONS
import logging

def execute_tool(tool_name, args):
    tool = TOOL_FUNCTIONS.get(tool_name)
    if not tool:
        logging.error(f"Tool {tool_name} not found.")
        return f"Error: Tool {tool_name} not found."

    try:
        if args:
            result = tool(**args)
        else:
            result = tool()
        return result
    except Exception as e:
        logging.error(f"Error executing tool {tool_name}: {e}")
        return f"Error executing tool '{tool_name}': {e}"