#!/bin/bash

# Utility: Print colored output
print_error() {
    echo -e "\033[31mError: $1\033[0m"
}

print_success() {
    echo -e "\033[32mSuccess: $1\033[0m"
}

print_warning() {
    echo -e "\033[33mWarning: $1\033[0m"
}
