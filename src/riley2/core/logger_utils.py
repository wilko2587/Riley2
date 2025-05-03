import logging
import sys
import os
import json
import inspect
import traceback
import platform
import shutil
from datetime import datetime
from colorama import Fore, Style, Back, init as colorama_init
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any, Optional, Union

colorama_init(autoreset=True)
IS_WINDOWS = platform.system() == 'Windows'

# Use platform-appropriate border characters
THIN_BORDER = '-' if IS_WINDOWS else '─'
THICK_BORDER = '=' if IS_WINDOWS else '═'
ARROW = '->'
TEST_PREFIX = '⟩⟩ TEST:'

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

LOG_COLORS = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    'PASSED': Back.GREEN + Fore.BLACK + Style.BRIGHT,
    'FAILED': Back.RED + Fore.WHITE + Style.BRIGHT,
    'JSON': Fore.LIGHTBLACK_EX
}

# Define terminal width function first before using it
def get_terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

# Now define the border using the function
SECTION_BORDER = f"{Fore.YELLOW}{THIN_BORDER * get_terminal_width()}{Style.RESET_ALL}"

def log_header(test_name):
    width = get_terminal_width()
    line = THICK_BORDER * width
    print(Fore.CYAN + line)
    print(Fore.CYAN + f"{TEST_PREFIX} {test_name}")

def log_footer_pass(test_name):
    print(LOG_COLORS['PASSED'] + f"[+] TEST PASSED: {test_name}" + Style.RESET_ALL)

def log_footer_fail(test_name):
    print(LOG_COLORS['FAILED'] + f"[-] TEST FAILED: {test_name}" + Style.RESET_ALL)

def log_json_block(obj):
    text = json.dumps(obj, indent=2)
    for line in text.splitlines():
        print(LOG_COLORS['JSON'] + f"  {line}")

def log(level, message):
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    color = LOG_COLORS.get(level, Fore.WHITE)
    print(f"{timestamp} | {color}{level:<5}{Style.RESET_ALL} | {message}")

# Setup Python's logging system alongside our custom logging
# Required for backward compatibility with conftest.py

# Custom formatter for logging that uses colorama
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        level_name = record.levelname
        if level_name in LOG_COLORS:
            message = message.replace(f"{level_name}", f"{LOG_COLORS[level_name]}{level_name}{Style.RESET_ALL}")
        return message

# Filter to exclude httpcore debug logs during testing
class HttpcoreFilter(logging.Filter):
    def filter(self, record):
        return not (record.name.startswith('httpcore') and record.levelname == 'DEBUG')

# Create main logger
logger = logging.getLogger("riley2")
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Create test-specific logger for compatibility
test_logger = logging.getLogger("riley2_test")
test_logger.setLevel(logging.DEBUG)
test_logger.propagate = False

# Clear any existing handlers
if logger.handlers:
    logger.handlers.clear()
if test_logger.handlers:
    test_logger.handlers.clear()

# Add a console handler by default
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s"))

logger.addHandler(console_handler)
test_logger.addHandler(console_handler)

def log_system_event(event_type: str, description: str):
    """Log system-level events like startup, shutdown, or configuration changes"""
    log("INFO", f"[SYSTEM - {event_type}] {description}")
    logger.info(f"[SYSTEM - {event_type}] {description}")

# Adding the missing functions that are imported in test files

def log_agent_interaction(agent_name: str, action: str, message: str, data=None):
    """Log interactions between agents in the system"""
    log_line = f"[AGENT - {agent_name}] {action}: {message}"
    logger.info(log_line)
    print(Fore.BLUE + f"[AGENT] {agent_name} | {action}" + Style.RESET_ALL)
    print(f"  {message}")
    if data:
        log_json_block(data)
    print(SECTION_BORDER)

def log_test_step(step_name: str, description: str = None):
    """Log a test step during test execution"""
    width = get_terminal_width() - 20
    step_line = f"TEST STEP: {step_name}"
    print(Fore.CYAN + "┌" + "─" * width + "┐")
    print(Fore.CYAN + "│" + f" {step_line}" + " " * (width - len(step_line) - 1) + "│")
    if description:
        desc_line = f"  {description}"
        print(Fore.CYAN + "│" + f" {desc_line}" + " " * (width - len(desc_line) - 1) + "│")
    print(Fore.CYAN + "└" + "─" * width + "┘")
    logger.info(f"[TEST] Step: {step_name} - {description if description else ''}")

def log_test_success(test_name: str, message: str = None):
    """Log a successful test completion"""
    success_msg = f"TEST SUCCESS: {test_name}"
    if message:
        success_msg += f" - {message}"
    print(LOG_COLORS['PASSED'] + success_msg + Style.RESET_ALL)
    logger.info(f"[TEST] Success: {test_name} - {message if message else ''}")

def log_test_failure(test_name: str, message: str = None, error=None):
    """Log a test failure with details"""
    failure_msg = f"TEST FAILURE: {test_name}"
    if message:
        failure_msg += f" - {message}"
    print(LOG_COLORS['FAILED'] + failure_msg + Style.RESET_ALL)
    logger.error(f"[TEST] Failure: {test_name} - {message if message else ''}")
    
    if error:
        err_text = str(error)
        for line in err_text.splitlines():
            print(Fore.RED + f"  {line}")
        logger.error(f"Error details: {err_text}")

def log_llm_call(model: str, prompt: str, response: str = None, metadata: dict = None):
    """Log LLM API calls with prompt, response and metadata"""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    print(f"{Fore.MAGENTA}[LLM CALL] {timestamp} - Model: {model}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}PROMPT:{Style.RESET_ALL}")
    print(f"{prompt[:500]}..." if len(prompt) > 500 else prompt)
    
    if response:
        print(f"{Fore.GREEN}RESPONSE:{Style.RESET_ALL}")
        print(f"{response[:500]}..." if len(response) > 500 else response)
    
    if metadata:
        print(f"{Fore.BLUE}METADATA:{Style.RESET_ALL}")
        log_json_block(metadata)
    
    print(SECTION_BORDER)
    
    # Also log to file for reference
    logger.debug(f"LLM Call - Model: {model}")
    logger.debug(f"Prompt: {prompt}")
    if response:
        logger.debug(f"Response: {response}")
    if metadata:
        logger.debug(f"Metadata: {json.dumps(metadata)}")

def log_decision_point(component: str, decision: str, options: List[str] = None, reason: str = None):
    """Log a decision point in the application flow with reasoning"""
    print(f"{Fore.YELLOW}[DECISION] {component}: {decision}{Style.RESET_ALL}")
    
    if options:
        print("Options considered:")
        for i, option in enumerate(options):
            if option == decision:
                print(f"  {i+1}. {Fore.GREEN}{option} [SELECTED]{Style.RESET_ALL}")
            else:
                print(f"  {i+1}. {option}")
    
    if reason:
        print(f"Reason: {reason}")
    
    print(SECTION_BORDER)
    logger.info(f"Decision in {component}: {decision}" + (f" - {reason}" if reason else ""))

def show_event_sequence(events_or_title: Union[List[Dict[str, Any]], str], title_or_events: Optional[Union[str, List[Dict[str, Any]]]] = None):
    """Display a sequence of events in a timeline format
    
    Can be called with either:
    - show_event_sequence(events_list) 
    - show_event_sequence(title_string, events_list)
    - show_event_sequence(events_list, title_string)
    """
    # Handle flexible parameter order
    if isinstance(events_or_title, str) and isinstance(title_or_events, list):
        # Called as show_event_sequence(title, events)
        title = events_or_title
        events = title_or_events
    elif isinstance(events_or_title, list) and (title_or_events is None or isinstance(title_or_events, str)):
        # Called as show_event_sequence(events, title) or just show_event_sequence(events)
        events = events_or_title
        title = title_or_events if title_or_events else "Event Sequence"
    else:
        # Fallback handling for unexpected parameter types
        logger.error(f"show_event_sequence called with invalid parameter types: {type(events_or_title)}, {type(title_or_events)}")
        if isinstance(events_or_title, list):
            events = events_or_title
            title = "Event Sequence"
        else:
            logger.error("Cannot display event sequence - invalid parameters")
            return
    
    width = get_terminal_width() - 10
    print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
    print(Fore.CYAN + "┌" + "─" * width + "┐")
    
    for i, event in enumerate(events):
        event_time = event.get('timestamp', 'N/A')
        event_type = event.get('type', 'EVENT')
        event_desc = event.get('description', 'No description')
        event_status = event.get('status', None)
        
        # Format event line with appropriate color based on event type or status
        if event_status == 'success':
            status_color = Fore.GREEN
        elif event_status == 'failure':
            status_color = Fore.RED
        elif event_status == 'warning':
            status_color = Fore.YELLOW
        else:
            status_color = Fore.WHITE
            
        timeline = f"│ {event_time} │ "
        print(f"{Fore.CYAN}│{Style.RESET_ALL} {i+1:2d}. {event_time} - {status_color}{event_type}{Style.RESET_ALL}: {event_desc}")
        
        # Show details if any
        if 'details' in event and event['details']:
            details = event['details']
            if isinstance(details, dict):
                for k, v in details.items():
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}      ↳ {k}: {v}")
            elif isinstance(details, (list, tuple)):
                for item in details:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}      ↳ {item}")
            else:
                print(f"{Fore.CYAN}│{Style.RESET_ALL}      ↳ {details}")
    
    print(Fore.CYAN + "└" + "─" * width + "┘")
    logger.info(f"Displayed event sequence: {title} with {len(events)} events")

def log_tool_usage(tool_name: str, inputs: Dict[str, Any] = None, outputs: Dict[str, Any] = None, success: bool = True):
    """Log tool usage with inputs and outputs"""
    status = "SUCCESS" if success else "FAILURE"
    color = Fore.GREEN if success else Fore.RED
    
    print(f"{color}[TOOL] {tool_name} - {status}{Style.RESET_ALL}")
    
    if inputs:
        print(f"{Fore.YELLOW}Inputs:{Style.RESET_ALL}")
        log_json_block(inputs)
    
    if outputs:
        print(f"{Fore.CYAN}Outputs:{Style.RESET_ALL}")
        # If outputs is large, truncate it for display
        if isinstance(outputs, dict) and any(isinstance(v, str) and len(v) > 500 for v in outputs.values()):
            truncated_outputs = {}
            for k, v in outputs.items():
                if isinstance(v, str) and len(v) > 500:
                    truncated_outputs[k] = v[:500] + "..."
                else:
                    truncated_outputs[k] = v
            log_json_block(truncated_outputs)
        else:
            log_json_block(outputs)
    
    print(SECTION_BORDER)
    
    # Log to file
    logger.info(f"Tool {tool_name} used - {status}")
    if inputs:
        logger.debug(f"Tool inputs: {json.dumps(inputs, default=str)}")
    if outputs:
        logger.debug(f"Tool outputs: {json.dumps(outputs, default=str)}")

def log_component_interaction(source: str, target: str, action: str, data: Any = None, result: Any = None, direction: str = None):
    """Log interactions between system components"""
    direction_arrow = direction if direction else f"{source} → {target}"
    print(f"{Fore.BLUE}[COMPONENT] {direction_arrow}: {action}{Style.RESET_ALL}")
    
    if data:
        print(f"{Fore.YELLOW}Data sent:{Style.RESET_ALL}")
        if isinstance(data, dict):
            log_json_block(data)
        else:
            print(f"  {data}")
    
    if result:
        print(f"{Fore.GREEN}Result:{Style.RESET_ALL}")
        if isinstance(result, dict):
            log_json_block(result)
        else:
            print(f"  {result}")
    
    print(SECTION_BORDER)
    
    # Log to file
    logger.info(f"Component interaction: {source} → {target}: {action}")
    if data:
        if isinstance(data, dict):
            logger.debug(f"Interaction data: {json.dumps(data, default=str)}")
        else:
            logger.debug(f"Interaction data: {data}")
    if result:
        if isinstance(result, dict):
            logger.debug(f"Interaction result: {json.dumps(result, default=str)}")
        else:
            logger.debug(f"Interaction result: {result}")
