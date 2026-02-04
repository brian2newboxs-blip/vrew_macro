#!/bin/bash

# Vrew Macro Launcher for macOS
# Detects CPU architecture and launches the appropriate version.

ARCH=$(uname -m)

echo "Detected Architecture: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "Launching Apple Silicon version..."
    if [ -d "Vrew_Macro_Silicon.app" ]; then
        open "Vrew_Macro_Silicon.app"
    else
        echo "Error: Vrew_Macro_Silicon.app not found!"
        exit 1
    fi
else
    echo "Launching Intel version..."
    if [ -d "Vrew_Macro_Intel.app" ]; then
        open "Vrew_Macro_Intel.app"
    else
        echo "Error: Vrew_Macro_Intel.app not found!"
        exit 1
    fi
fi
