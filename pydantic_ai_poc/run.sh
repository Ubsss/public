#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

############################################################
# run docker-compose
############################################################

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Error: Docker is not installed or not in PATH."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null
then
    echo "Error: Docker does not appear to be running."
    exit 1
fi

# Check if a docker-compose file exists
if [[ ! -f "docker-compose.yml" && ! -f "docker-compose.yaml" ]]; then
    echo "Error: No docker-compose.yml or docker-compose.yaml found in current directory."
    exit 1
fi

# Run docker-compose in detached mode
echo "Starting Docker containers via docker-compose..."
docker-compose up -d

############################################################
# run python
############################################################

# Check if python3 is installed.
if ! command -v python &> /dev/null
then
    echo "Error: python is not installed or not in PATH."
    exit 1
fi

# Create a virtual environment if it doesn't already exist.
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Detect OS and activate the virtual environment.
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Darwin*)    MACHINE="Mac";;
    Linux*)     MACHINE="Linux";;
    CYGWIN*|MINGW*|MSYS*)    MACHINE="Windows";;
    *)          MACHINE="Unknown";;
esac

echo "Detected OS: $MACHINE"

if [ "$MACHINE" = "Windows" ]; then
    # On Windows (Git Bash / MSYS / Cygwin), the activation script is in venv/Scripts/activate
    source venv/Scripts/activate
elif [ "$MACHINE" = "Mac" ] || [ "$MACHINE" = "Linux" ]; then
    # On macOS or Linux, the activation script is usually in venv/bin/activate
    source venv/bin/activate
else
    echo "Error: Unknown or unsupported OS. Exiting..."
    exit 1
fi

# Install dependencies from requirements.txt.
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Skipping dependency installation."
fi

# Set environment variables (customize as needed).
echo "Setting environment variables..."
export OLLAMA_ENDPOINT="http://localhost:11434"
export MODEL_NAME="mistral:7b"
export SYSTEM_PROMPT="You are great a solving problems in a friendly way."

# Run Python script.
echo "Running Python script..."
python frontend.py