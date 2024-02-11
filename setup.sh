#!/bin/bash

# Define main variables
REQUIREMENTS_FILE="requirments.txt"
MAIN_FOLDER="folders"
SUBFOLDERS=("in" "results" "tmp")

# Function to check for command existence
function check_command() {
    command -v $1 >/dev/null 2>&1 || { echo >&2 "I require $1 but it's not installed. Aborting."; exit 1; }
}

# Function to install Python packages
function install_requirements() {
    echo "Installing requirements from $REQUIREMENTS_FILE..."
    python3 -m pip install -r $REQUIREMENTS_FILE || { echo "Failed to install requirements. Aborting."; exit 1; }
}

# Function to create folders
function create_folders() {
    for folder in "${SUBFOLDERS[@]}"; do
        mkdir -p "$MAIN_FOLDER/$folder"
        echo "Created $MAIN_FOLDER/$folder"
    done
}

# Main script execution starts here

# Check necessary commands
check_command python3
check_command pip

# Install Python packages
install_requirements

# Create main folder and sub-folders
echo "Setting up folder structure..."
mkdir -p "$MAIN_FOLDER"
create_folders

echo "Setup complete."
