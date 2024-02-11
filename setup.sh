#!/bin/bash

# Path to the requirements file
REQUIREMENTS_FILE="requirments.txt"

# The main folder name
MAIN_FOLDER="folders"

# Sub-folders to create inside the main folder
FOLDERS=("in" "results" "tmp")

# Install packages from the requirements file using pip
echo "Installing requirements from $REQUIREMENTS_FILE..."
pip install -r $REQUIREMENTS_FILE

# Check if the main folder already exists. If not, create it.
if [ ! -d "$MAIN_FOLDER" ]; then
    echo "Creating $MAIN_FOLDER folder..."
    mkdir "$MAIN_FOLDER"
else
    echo "$MAIN_FOLDER folder already exists."
fi

# Create sub-folders inside the main folder
for FOLDER in "${FOLDERS[@]}"; do
    if [ ! -d "$MAIN_FOLDER/$FOLDER" ]; then
        echo "Creating $FOLDER folder inside $MAIN_FOLDER..."
        mkdir "$MAIN_FOLDER/$FOLDER"
    else
        echo "$FOLDER folder already exists inside $MAIN_FOLDER."
    fi
done

echo "Setup complete."
