#!/usr/bin/env python
"""
Script to tail logs with detailed information and color highlighting
This script will show all the important information including:
- LLM inputs/outputs
- Agent interactions
- Backend manager loops
- Keyword matching logic
"""

import os
import sys
import time
import re
from datetime import datetime
from colorama import Fore, Style, init as colorama_init

# Initialize colorama for cross-platform color support
colorama_init(autoreset=True)

# Color definitions for different log components
COLORS = {
    'timestamp': Fore.MAGENTA,
    'level': {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    },
    'component': {
        'LLM': Fore.BLUE + Style.BRIGHT,
        'Agent': Fore.CYAN,
        'Backend': Fore.GREEN,
        'Tool': Fore.YELLOW,
        'Decision': Fore.MAGENTA
    },
    'direction': {
        '>>>': Fore.YELLOW,
        '<<<': Fore.CYAN,
        'INPUT': Fore.YELLOW,
        'OUTPUT': Fore.CYAN,
        'ARGS': Fore.YELLOW,
        'RESULT': Fore.CYAN
    },
    'default': Fore.WHITE
}

def colorize_log_line(line):
    """Apply color highlighting to different parts of a log line"""
    if not line.strip():
        return line
    
    # Extract and colorize timestamp if present
    timestamp_match = re.match(r'^([\d-]+ [\d:]+) - ', line)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
        line = line.replace(timestamp, f"{COLORS['timestamp']}{timestamp}{Style.RESET_ALL}", 1)
    
    # Colorize log levels
    for level, color in COLORS['level'].items():
        if f" - {level} - " in line:
            line = line.replace(f" - {level} - ", f" - {color}{level}{Style.RESET_ALL} - ", 1)
    
    # Highlight components and tags in brackets
    bracket_pattern = r'\[([^\]]+)\]'
    for match in re.finditer(bracket_pattern, line):
        tag = match.group(1)
        
        # Choose color based on component type
        color = COLORS['default']
        for component, comp_color in COLORS['component'].items():
            if component.lower() in tag.lower():
                color = comp_color
                break
                
        # Replace with colored version
        original = match.group(0)
        colored = f"[{color}{tag}{Style.RESET_ALL}]"
        line = line.replace(original, colored, 1)
    
    # Highlight directional indicators
    for direction, color in COLORS['direction'].items():
        if f" >>> " in line:
            line = line.replace(" >>> ", f" {color}>>>{Style.RESET_ALL} ", 1)
        if f" <<< " in line:
            line = line.replace(" <<< ", f" {color}<<<{Style.RESET_ALL} ", 1)
        
        # Look for INPUT/OUTPUT/ARGS/RESULT patterns
        if f": {direction}:" in line:
            line = line.replace(f": {direction}:", f": {color}{direction}{Style.RESET_ALL}:", 1)
    
    return line

def tail_log_file(file_path, num_lines=50, follow=True, filter_pattern=None):
    """Show the last N lines of a log file and optionally follow it"""
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Error: Log file not found: {file_path}{Style.RESET_ALL}")
        return
    
    # Get the initial set of lines
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        # Show the last num_lines
        start_idx = max(0, len(lines) - num_lines)
        for line in lines[start_idx:]:
            if filter_pattern is None or re.search(filter_pattern, line, re.IGNORECASE):
                print(colorize_log_line(line.rstrip()))
    
    # If follow mode is enabled, continue monitoring the file
    if follow:
        print(f"\n{Fore.YELLOW}Watching for new log entries... (Ctrl+C to exit){Style.RESET_ALL}")
        last_size = os.path.getsize(file_path)
        
        try:
            while True:
                if os.path.getsize(file_path) > last_size:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        f.seek(last_size)
                        new_lines = f.readlines()
                        for line in new_lines:
                            if filter_pattern is None or re.search(filter_pattern, line, re.IGNORECASE):
                                print(colorize_log_line(line.rstrip()))
                    last_size = os.path.getsize(file_path)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}Log viewing stopped.{Style.RESET_ALL}")

def list_log_files():
    """List all available log files in the logs directory"""
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        print(f"{Fore.RED}Logs directory not found{Style.RESET_ALL}")
        return
        
    print(f"\n{Fore.CYAN}Available log files:{Style.RESET_ALL}")
    log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')])
    
    for i, file_name in enumerate(log_files):
        file_path = os.path.join(log_dir, file_name)
        size_kb = os.path.getsize(file_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Highlight current run logs
        if "run_" in file_name and datetime.now().strftime('%Y%m%d') in file_name:
            print(f"{Fore.GREEN}{i+1}. {file_name} ({size_kb:.1f} KB) - {mtime}{Style.RESET_ALL}")
        else:
            print(f"{i+1}. {file_name} ({size_kb:.1f} KB) - {mtime}")
    
    return log_files

def main():
    """Parse arguments and run the log viewer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="View Riley2 logs with color highlighting")
    parser.add_argument('-f', '--file', help='Log file to view (number or path)')
    parser.add_argument('-n', '--lines', type=int, default=50, help='Number of lines to show initially')
    parser.add_argument('-s', '--search', help='Filter logs by search pattern')
    parser.add_argument('--no-follow', action='store_true', help='Don\'t follow the log file for new entries')
    
    args = parser.parse_args()
    
    # List available log files first
    log_files = list_log_files()
    
    # Determine which log file to view
    log_file = None
    if args.file:
        if args.file.isdigit() and 1 <= int(args.file) <= len(log_files):
            # User specified a number corresponding to a log file
            log_file = os.path.join('logs', log_files[int(args.file) - 1])
        elif os.path.exists(args.file):
            # User specified a direct path
            log_file = args.file
        elif os.path.exists(os.path.join('logs', args.file)):
            # User specified just the file name
            log_file = os.path.join('logs', args.file)
    
    # If no file specified or found, use the latest run log
    if log_file is None:
        # Find the most recent run log file
        run_logs = [f for f in log_files if f.startswith('riley2_run_') or f.startswith('riley2_detailed')]
        if run_logs:
            log_file = os.path.join('logs', run_logs[0])
        elif log_files:
            log_file = os.path.join('logs', log_files[0])
        else:
            print(f"{Fore.RED}No log files found{Style.RESET_ALL}")
            return
    
    print(f"\n{Fore.GREEN}Viewing log: {log_file}{Style.RESET_ALL}")
    if args.search:
        print(f"{Fore.YELLOW}Filtering for: {args.search}{Style.RESET_ALL}")
    
    # View the log file
    tail_log_file(log_file, args.lines, not args.no_follow, args.search)

if __name__ == '__main__':
    main()