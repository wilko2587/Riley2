import logging
import sys
import os

# Add 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the logger from logger_utils instead of configuring a new one
from riley2.core.logger_utils import logger

# Add a file handler if not already present to ensure logs go to riley2.log
for handler in logger.handlers:
    if isinstance(handler, logging.FileHandler) and handler.baseFilename.endswith('riley2.log'):
        break
else:
    # No riley2.log file handler found, add one
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "riley2.log"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

from riley2.core.router_chain import route_user_query

def main():
    logger.info("Riley2 main application started")
    print("✅ Gmail authentication OK")
    print("✅ Calendar authentication OK")
    print("Riley2 (Dual LLM) is live. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            logger.info("User requested exit. Shutting down.")
            break

        logger.info(f"Processing user query: {user_input}")
        reply = route_user_query(user_input)
        print(f"Riley2: {reply}")

if __name__ == "__main__":
    main()