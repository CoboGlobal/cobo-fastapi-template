#!/bin/bash

# Load modules
SCRIPT_DIR=$(dirname "$(realpath "$0")")

source "$SCRIPT_DIR/venv_manager.sh"
source "$SCRIPT_DIR/config_manager.sh"
source "$SCRIPT_DIR/dependency_manager.sh"
source "$SCRIPT_DIR/service_manager.sh"
source "$SCRIPT_DIR/check_cobo_cli.sh"
source "$SCRIPT_DIR/utils.sh"

# Default configurations
PORT=8000
ENV="dev" # Default environment

# Valid environments
VALID_ENVS=("sandbox" "dev" "prod")

# Log file
LOG_FILE="setup.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# Function: Validate environment
validate_env() {
    local env=$1
    for valid_env in "${VALID_ENVS[@]}"; do
        if [[ "$env" == "$valid_env" ]]; then
            return 0
        fi
    done
    return 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift 2 ;;
        --env) ENV="$2"; shift 2 ;;
        --help)
            echo "Usage: $0 [--port PORT] [--env sandbox|dev|prod]"
            exit 0
            ;;
        *)
            print_error "Unknown parameter: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Validate the environment
if ! validate_env "$ENV"; then
    print_error "Invalid environment: $ENV"
    echo "Valid environments are: sandbox, dev, prod"
    exit 1
fi

# Main Logic
echo "============================="
echo "Starting setup..."
echo "Environment: $ENV"
echo "Port: $PORT"
echo "============================="

# Step 1: Check cobo-cli installation
check_cobo || exit 1

# Step 2: Virtual Environment Management
manage_virtual_environment || exit 1

# Step 3: Setup .env file
ensure_key_and_secret "$ENV" || exit 1

# Step 4: Install dependencies
install_dependencies || exit 1

# Step 5: Check if the port is available
check_port_availability "$PORT" || exit 1

# Step 6: Start the application
start_application "$PORT"
