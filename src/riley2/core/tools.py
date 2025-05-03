# core/tools.py

from riley2.core.tool_registry import TOOL_FUNCTIONS
from riley2.agents.backend_director_agent import handle_backend_query

# TOOL_FUNCTIONS contains all basic tools: email, calendar, kdb, etc.
# backend_director is for advanced queries that require chaining/multi-tool reasoning

TOOLS = {
    **TOOL_FUNCTIONS,
    "backend_director": handle_backend_query,
}
