#!/bin/bash

# Default port
PORT=8000

# Parse the incoming arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift ;;
    esac
    shift
done

CREATE_VENV=0

if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "No active Python virtual environment detected."
  CREATE_VENV=1
else
  if [[ -d "venv" ]]; then
      source venv/bin/activate
  else
    echo "You are in an exist Python virtual environment. Are you willing to install dependencies to current virtual environment?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) exit;;
            No ) CREATE_VENV=1; break;;
        esac
    done
  fi
fi

if [[ "$CREATE_VENV" == 1 ]]; then
  # Check if venv directory exists
  if [[ ! -d "venv" ]]; then
      echo "Creating a new Python virtual environment..."
      python3 -m venv venv
  fi

  # Activate the virtual environment
  source venv/bin/activate
fi

# Check and install dependencies
if [[ -f "requirements.txt" ]]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt file not found, skipping dependency installation."
fi

# Change directory and start the app
cd app && uvicorn main:app --reload --port "$PORT"
