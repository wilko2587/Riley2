from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from riley2.core.logger_utils import logger, log_agent_interaction

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

def summarize_text(text, verbose=False):
    logger.debug(f"Summarize text called with: {text[:100]}{'...' if len(text) > 100 else ''}")
    if verbose: logger.info(f"[LLM Prompt Input] {text}")
    raw_result = backend_chain.invoke({
        "tool": "summarize_email",
        "args": text,
        "output": text
    })
    logger.debug(f"Summarization result: {raw_result}")
    if verbose: logger.info(f"[LLM Raw Output] {raw_result}")
    result = raw_result.content
    if verbose: logger.info(f"[LLM Final Output]: {result}")
    return result

def interpret_tool_command(tool_name, args, result):
    logger.debug(f"Interpreting tool command: {tool_name} with args: {args} and result: {result}")
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

    logger.debug(f"Interpretation complete for tool: {tool_name}")
    logger.debug(f"[interpret_tool_command] Final Response: {output}")
    return output

# Smarter backend agent logic
class BackendLLM:
    def choose_next_action(self, query, context):
        logger.debug(f"Choosing next action for query: {query} with context: {context}")
        lowered = query.lower()
        if "italy" in lowered or "trip" in lowered or "travel" in lowered:
            action = "calendar_search"
        elif "next" in lowered or "soon" in lowered or "coming up" in lowered:
            action = "calendar_next"
        elif "email" in lowered:
            action = "email_search"
        elif "knowledge" in lowered or "kdb" in lowered:
            action = "kdb_lookup"
        else:
            action = "calendar_next"
        logger.debug(f"Next action chosen: {action}")
        return action

    def get_decision(self, prompt):
        logger.debug(f"Getting decision for prompt: {prompt}")
        if "enough information" in prompt.lower():
            decision = "yes"
        else:
            decision = "yes"
        logger.debug(f"Decision made: {decision}")
        return decision

backend_llm = BackendLLM()

def backend_planner_llm(prompt, verbose=False):
    logger.debug(f"Backend planner LLM called with prompt: {prompt}")
    local_llm = ChatOllama(model="mistral", temperature=0.2)
    result = local_llm.invoke(prompt).content

    logger.debug(f"Planner LLM result: {result}")

    if verbose:
        print("\n[LLM RESPONSE]")
        print(result)
        print("\n")

    return result
