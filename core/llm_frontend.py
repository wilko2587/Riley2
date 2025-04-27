from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory


# Define the LLM used for routing
llm = ChatOllama(model="mistral", temperature=0.1)

# Basic conversational memory (can later be persisted)
memory = ConversationBufferMemory(return_messages=True)

# Prompt to guide the router LLM to choose the correct tool
router_prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("system", """
        You are Riley2, a personal assistant AI.

        Based on the user's input below, decide what tool should be used.
        Only return one of the following tool names (in lowercase, no punctuation):

        - email_inbox
        - email_latest
        - email_unread
        - email_search
        - calendar_range
        - calendar_next
        - calendar_search
        - kdb_query
        - kdb_add_entry
        - kdb_edit_entry
        - kdb_delete_entry

        If the input doesn't clearly map to a tool, respond with: fallback
    """),
    ("human", "{user_input}")
])

# Tool routing chain
router_chain = RunnableSequence(router_prompt | llm)
