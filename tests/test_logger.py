import os
import logging
import sys
from colorama import Fore, Style, init as colorama_init

# Initialize colorama for cross-platform ANSI color support
colorama_init(autoreset=True)

# Color mapping for different log levels
LOG_COLORS = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.MAGENTA + Style.BRIGHT
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages based on level"""
    
    def format(self, record):
        levelname = record.levelname
        if levelname in LOG_COLORS:
            levelname_color = LOG_COLORS[levelname] + levelname + Style.RESET_ALL
            record.levelname = levelname_color
        return super().format(record)

def setup_test_logger(log_path='logs/riley2_test.log', enable_console=True, enable_color=True):
    """Set up a logger that writes to file and optionally to console with color"""
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger('riley2_test')
    
    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
        
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler(log_path)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)
    
    # Console handler with color support
    if enable_console:
        console = logging.StreamHandler(sys.stdout)
        if enable_color:
            console_format = '%(asctime)s - %(levelname)s - %(message)s'
            console_formatter = ColoredFormatter(console_format, datefmt='%Y-%m-%d %H:%M:%S')
        else:
            console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console.setFormatter(console_formatter)
        logger.addHandler(console)
    
    return logger

# For direct script execution - test the colored logger
if __name__ == '__main__':
    logger = setup_test_logger()
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
