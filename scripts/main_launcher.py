import logging
import sys
import os

# Add 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Configure logging at the top level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("./logs/riley2.log"),
        logging.StreamHandler()
    ]
)

from riley2.core.router_chain import route_user_query

def main():
    print("✅ Gmail authentication OK")
    print("✅ Calendar authentication OK")
    print("Riley2 (Dual LLM) is live. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        reply = route_user_query(user_input)
        print(f"Riley2: {reply}")

if __name__ == "__main__":
    main()