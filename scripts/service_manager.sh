#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/utils.sh"

# Function: Check if port is in use
check_port_availability() {
    local port=$1
    if lsof -i:"$port" &>/dev/null; then
        print_error "Port $port is already in use. Please choose a different port with --port option."
        exit 1
    fi
}

# Function: Start the application
start_application() {
    local port=$1
    echo "Starting the application on port $port..."
    uvicorn app.main:app --reload --port "$port"
}
