#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/utils.sh"

# Function: Check if cobo CLI is installed
check_cobo() {
    echo "Checking if cobo CLI is installed..."

    # Check if cobo command exists using `cobo -v`
    if ! cobo version &>/dev/null; then
        print_warning "Cobo CLI is not installed."

        # Check availability of installation methods
        local has_pip=0
        local has_brew=0

        if command -v pip &>/dev/null; then
            has_pip=1
        fi
        if command -v brew &>/dev/null; then
            has_brew=1
            if ! brew search cobo-cli &>/dev/null; then
                has_brew=0  # Homebrew does not support cobo-cli
            fi
        fi

        # Inform user of available installation methods
        if [[ "$has_pip" -eq 1 ]] || [[ "$has_brew" -eq 1 ]]; then
            echo "You can install cobo CLI using one of the following methods:"
            if [[ "$has_pip" -eq 1 ]]; then
                echo "1. Install via pip: pip install cobo-cli"
            fi
            if [[ "$has_brew" -eq 1 ]]; then
                echo "2. Install via Homebrew: brew install cobo-cli"
            fi

            # Ask user for installation preference
            while true; do
                if [[ "$has_pip" -eq 1 && "$has_brew" -eq 1 ]]; then
                    read -p "Choose an installation method (1 for pip, 2 for Homebrew): " choice
                elif [[ "$has_pip" -eq 1 ]]; then
                    choice=1
                elif [[ "$has_brew" -eq 1 ]]; then
                    choice=2
                else
                    break
                fi

                case "$choice" in
                    1 )
                        echo "Installing cobo CLI using pip..."
                        pip install cobo-cli || {
                            print_error "Error: Failed to install cobo CLI using pip."
                            exit 1
                        }
                        break
                        ;;
                    2 )
                        echo "Installing cobo CLI using Homebrew..."
                        brew install cobo-cli || {
                            print_error "Error: Failed to install cobo CLI using Homebrew."
                            exit 1
                        }
                        break
                        ;;
                    * )
                        print_error "Invalid choice. Please choose 1 for pip or 2 for Homebrew."
                        ;;
                esac
            done

            # Verify installation
            if cobo -v &>/dev/null; then
                print_success "Cobo CLI installed successfully."
            else
                print_error "Error: Failed to verify cobo CLI installation. Please install it manually."
                exit 1
            fi
        else
            print_error "Error: Neither pip nor Homebrew is available. Please install cobo CLI manually."
            exit 1
        fi
    else
        print_success "Cobo CLI is already installed."
    fi
}
