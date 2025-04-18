from core.ollama_interface import ask_llm
from core.agent_manager import handle_user_input

def chat_loop():
    print("Welcome to Riley2 (Multi-Agent AI Assistant)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Riley2: Goodbye!")
            break
        response = handle_user_input(user_input)
        print(f"Riley2: {response}")
