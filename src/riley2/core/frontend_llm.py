import logging
from .logger_utils import logger
from langchain_ollama import ChatOllama

def frontend_llm_response(user_query):
    logger.debug(f"Frontend LLM called with user query: {user_query}")
    llm = ChatOllama(model="mistral", temperature=0.7)  # Higher temperature for natural talk
    prompt = f"""
You are Riley2's Frontend LLM.
You handle casual conversation with the user and polish structured backend results nicely.

User says:
"{user_query}"

Respond naturally, warmly, and conversationally.
"""
    response = llm.invoke(prompt).content
    logger.debug(f"Frontend LLM response: {response}")
    return response