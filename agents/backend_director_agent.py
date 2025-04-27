from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnableSequence
from core.tool_executor import execute_tool

llm = ChatOllama(model="mistral", temperature=0.4)

# Step 1: Planner prompt – decides what to ask the backend agent
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     """
     You are a planning assistant for Riley2. Your job is to break down the user’s complex request into clear backend tool calls.
     For each step, suggest a JSON-formatted dictionary like:
     {"tool": "calendar_query", "args": {"query": "next weekend events"}}
     You may return multiple tool queries, separated by newlines if needed.
     Only return tool calls, no explanations.
     """),
    ("human", "{user_input}")
])
planner_chain = planner_prompt | llm

# Step 2: Summarizer prompt – interprets results into a final response
summarizer_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="intermediate_steps"),
    ("human", "Using the tool outputs above, answer the original user query: {original_question}")
])
summarizer_chain = summarizer_prompt | llm

# Main callable
def handle_backend_query(user_input: str) -> str:
    # Step 1: Generate tool call plan
    plan_raw = planner_chain.invoke({"user_input": user_input})
    tool_queries = parse_tool_queries(plan_raw)

    # Step 2: Execute each tool and collect outputs
    steps = []
    for query in tool_queries:
        tool = query.get("tool")
        args = query.get("args", {})
        result = execute_tool(tool, args)
        steps.append({"tool": tool, "args": args, "result": result})

    # Step 3: Summarize the results into a final user-facing response
    final = summarizer_chain.invoke({
        "intermediate_steps": steps,
        "original_question": user_input
    })
    return final.content.strip()


def parse_tool_queries(response_text):
    import json
    tool_calls = []
    for line in response_text.strip().splitlines():
        try:
            tool_calls.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return tool_calls
