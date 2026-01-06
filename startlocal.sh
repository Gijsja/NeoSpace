#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# Check for venv
if [ ! -f ".venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Please run: ./scripts/setup_venv.sh"
    exit 1
fi

source .venv/bin/activate
echo "Starting LocalBBS..."
python3 startlocal.py
