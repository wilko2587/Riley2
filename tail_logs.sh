#!/bin/bash

# Script to tail log files with color highlighting
# Usage: ./tail_logs.sh [log_file_path] [lines]

# Default log file and number of lines
LOG_FILE="logs/riley2_detailed.log"
LINES=50

# Override defaults if arguments provided
if [ ! -z "$1" ]; then
  LOG_FILE="$1"
fi

if [ ! -z "$2" ]; then
  LINES="$2"
fi

# ANSI color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Function to colorize output
colorize() {
  # Color error and warning messages
  sed -E "s/(ERROR|CRITICAL)/\${RED}&\${RESET}/g" | \
  sed -E "s/(WARNING)/\${YELLOW}&\${RESET}/g" | \
  sed -E "s/(INFO)/\${GREEN}&\${RESET}/g" | \
  sed -E "s/(DEBUG)/\${CYAN}&\${RESET}/g" | \
  # Highlight important tags
  sed -E "s/\[(.*?)\]/[\${BLUE}\1\${RESET}]/g" | \
  # Highlight timestamps
  sed -E "s/([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})/\${MAGENTA}\1\${RESET}/g"
}

echo -e "${GREEN}Tailing ${LINES} lines of ${LOG_FILE}...${RESET}"

if [ -f "$LOG_FILE" ]; then
  # Initial display with specified number of lines
  tail -n "$LINES" "$LOG_FILE" | colorize
  
  # Continue watching for changes
  echo -e "${YELLOW}Watching for new log entries... (Ctrl+C to exit)${RESET}"
  tail -f "$LOG_FILE" | colorize
else
  echo -e "${RED}Error: Log file '${LOG_FILE}' not found${RESET}"
  echo -e "${YELLOW}Available log files:${RESET}"
  find logs -type f -name "*.log" | sort
  exit 1
fi