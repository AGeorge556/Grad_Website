#!/bin/bash

echo "===== Dependency Conflict Fix Script ====="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Please install Python 3 or make sure it's in your PATH."
    exit 1
fi

echo "Choose a fix method:"
echo "1. Standard fix (tries to maintain version ranges)"
echo "2. Alternative fix (uses specific older versions)"
echo

read -p "Enter your choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo
    echo "Running standard dependency fix script..."
    python3 fix_dependencies.py
elif [ "$choice" = "2" ]; then
    echo
    echo "Running alternative dependency fix script..."
    python3 fix_dependencies_alt.py
else
    echo
    echo "Invalid choice. Please run the script again and enter 1 or 2."
    exit 1
fi

# Check if the script ran successfully
if [ $? -ne 0 ]; then
    echo
    echo "Failed to fix dependencies. Please check the error messages above."
    echo "Try the other fix method or contact support."
    exit 1
fi

echo
echo "Dependencies fixed successfully!"
echo
echo "You can now run your application without conflicts." 