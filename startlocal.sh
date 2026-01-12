#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Check for venv (Look for fix first, then standard)
VENV_DIR=".venv_fix"
if [ ! -d "$VENV_DIR" ]; then
    VENV_DIR=".venv"
fi

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Please run: python3 -m venv .venv_fix && source .venv_fix/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source $VENV_DIR/bin/activate
echo "Starting NeoSpace (Env: $VENV_DIR)..."
python3 startlocal.py
