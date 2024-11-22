#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/utils.sh"


# Function: Create and activate a virtual environment
create_and_activate_venv() {
    print_warning "Creating a new Python virtual environment..."
    python3 -m venv venv
    echo "Activating the virtual environment..."
    source venv/bin/activate
}

# Function: Activate an existing virtual environment
activate_existing_venv() {
    echo "Activating the existing virtual environment..."
    source venv/bin/activate
}

# Function: Manage virtual environment
manage_virtual_environment() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        if [[ -d "venv" ]]; then
            activate_existing_venv
        else
            create_and_activate_venv
        fi
    else
        print_warning "Using the active virtual environment: $VIRTUAL_ENV"
        while true; do
            read -p "Do you want to use the current virtual environment? (Y/n): " answer
            case $answer in
                [Yy]*) break ;;
                [Nn]*)
                  if [[ -d "venv" ]]; then
                      activate_existing_venv
                  else
                      create_and_activate_venv
                  fi
                  break ;;
                *) print_error "Invalid input. Please enter Y/y or N/n." ;;
            esac
        done
    fi
}
