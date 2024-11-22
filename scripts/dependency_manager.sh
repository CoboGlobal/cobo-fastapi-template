#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/utils.sh"

# Function: Install dependencies
install_dependencies() {
    if [[ -f "requirements.txt" ]]; then
        print_warning "Installing dependencies from requirements.txt..."
        if ! pip install -r requirements.txt; then
            print_error "Dependency installation failed. Please check the error messages above."
            exit 1
        fi
    else
        print_warning "requirements.txt not found. Skipping dependency installation."
    fi
}
