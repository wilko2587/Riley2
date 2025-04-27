# FINAL fixed logger_utils.py with safe console and file logging for Windows

import logging
import sys
import os
from datetime import datetime
from colorama import Fore, Style, init as colorama_init

colorama_init()

# Dynamically calculate base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Setup main logger
logger = logging.getLogger("riley2")
logger.setLevel(logging.DEBUG)

# Only add handlers once
if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Timestamped file handler
    log_filename = os.path.join(LOG_DIR, f'test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Steady file handler (riley2_test.log)
    steady_log_file = os.path.join(LOG_DIR, 'riley2_test.log')
    steady_file_handler = logging.FileHandler(steady_log_file, mode='a', encoding='utf-8')
    steady_file_handler.setLevel(logging.DEBUG)

    # Formatters
    class ConsoleFormatter(logging.Formatter):
        def format(self, record):
            if record.levelno == logging.DEBUG:
                return Fore.CYAN + f"[DEBUG] {record.getMessage()}" + Style.RESET_ALL
            elif record.levelno == logging.INFO:
                return Fore.GREEN + f"[INFO] {record.getMessage()}" + Style.RESET_ALL
            elif record.levelno == logging.WARNING:
                return Fore.YELLOW + f"[WARNING] {record.getMessage()}" + Style.RESET_ALL
            elif record.levelno == logging.ERROR:
                return Fore.RED + f"[ERROR] {record.getMessage()}" + Style.RESET_ALL
            elif record.levelno == logging.CRITICAL:
                return Fore.RED + Style.BRIGHT + f"[CRITICAL] {record.getMessage()}" + Style.RESET_ALL
            else:
                return f"[{record.levelname}] {record.getMessage()}"

    file_formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')

    console_handler.setFormatter(ConsoleFormatter())
    file_handler.setFormatter(file_formatter)
    steady_file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(steady_file_handler)

# Helper functions for agents and tests
def log_agent_interaction(agent_name: str, role: str, message: str):
    formatted = f"[{agent_name} - {role}] >>> {message}"
    logger.info(formatted)

def log_test_step(step_description: str):
    formatted = f"💠 TEST STEP >>> {step_description}"
    logger.info(formatted)

def log_test_success(test_name: str):
    formatted = f"✅ TEST PASSED >>> {test_name}"
    logger.info(formatted)

# Capture uncaught exceptions into logger
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception