#!/usr/bin/env bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}==> Setting up LocalBBS Environment compatibility layer...${NC}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-test.txt

echo -e "${GREEN}==> Setup complete!${NC}"
echo "Run './startlocal.sh' to launch the server."
