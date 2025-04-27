from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from core.logger_utils import logger, log_agent_interaction

# Initialize LLM
llm = ChatOllama(model="mistral", temperature=0.4)

backend_prompt = PromptTemplate(
    input_variables=["tool", "args", "output"],
    template="""
You are Riley2, a helpful AI assistant. Your task is to interpret the results of tools and explain them to the user in natural language.

Tool used: {tool}
Arguments: {args}
Raw tool output:
{output}

Please turn this into a human-readable, conversational response.
"""
)

backend_chain = backend_prompt | llm

def summarize_text(text):
    logger.debug(f"[summarize_text] Input text: {text}")
    raw_result = backend_chain.invoke({
        "tool": "summarize_email",
        "args": text,
        "output": text
    })
    logger.debug(f"[summarize_text] Raw Output: {raw_result}")
    result = raw_result.content
    logger.debug(f"[summarize_text] Final Content: {result}")
    return result

def interpret_tool_command(tool_name, args, result):
    logger.debug(f"[interpret_tool_command] tool_name: {tool_name}, args: {args}, result: {result}")

    local_llm = ChatOllama(model="mistral", temperature=0.7)

    prompt = PromptTemplate.from_template(
        "You are Riley2. A user asked to use the tool '{tool_name}' with arguments {args}. "
        "The tool returned this result:\n\n{result}\n\n"
        "Craft a clear, human-sounding response to summarize the result to the user."
    )

    local_backend_chain = prompt | local_llm

    output = local_backend_chain.invoke({
        "tool_name": tool_name,
        "args": args,
        "result": result
    }).content

    logger.debug(f"[interpret_tool_command] Final Response: {output}")
    return output

# Smarter backend agent logic
class BackendLLM:
    def choose_next_action(self, query, context):
        lowered = query.lower()
        if "italy" in lowered or "trip" in lowered or "travel" in lowered:
            return "calendar_search"
        if "next" in lowered or "soon" in lowered or "coming up" in lowered:
            return "calendar_next"
        if "email" in lowered:
            return "email_search"
        if "knowledge" in lowered or "kdb" in lowered:
            return "kdb_lookup"
        return "calendar_next"

    def get_decision(self, prompt):
        if "enough information" in prompt.lower():
            return "yes"
        return "yes"

backend_llm = BackendLLM()

def backend_planner_llm(prompt):
    local_llm = ChatOllama(model="mistral", temperature=0.2)
    result = local_llm.invoke(prompt).content
    logger.debug(f"[backend_planner_llm] Planner Response: {result}")
    return result
