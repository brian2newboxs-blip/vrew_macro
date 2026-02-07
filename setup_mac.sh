#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi

# Make .command files executable
echo "Making .command files executable..."
chmod +x Run_Original.command
chmod +x Run_Vrew_Macro.command
chmod +x mac_launcher.sh

echo "Setup complete! You can now run the macro using Run_Original.command or Run_Vrew_Macro.command"
