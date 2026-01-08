#!/usr/bin/env bash
# =============================================================
# NeoSpace Production Server — Gunicorn gthread
# =============================================================
# Handles ~64 concurrent active requests.
# Flask-SocketIO manages idle WebSocket connections.
# Target: ~2,000 users on 2013 hardware.
# =============================================================

set -e
cd "$(dirname "$0")"

# Check for venv
if [ ! -f ".venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Please run: ./scripts/setup_venv.sh"
    exit 1
fi

source .venv/bin/activate

echo "Starting NeoSpace (Production Mode)..."
echo "Workers: 4, Threads: 16, Worker Class: gthread"

# Set Flask-SocketIO to threading mode for gthread compatibility
export SOCKETIO_ASYNC_MODE=threading

# Gunicorn with gthread — solves SQLite blocking issues
# --worker-tmp-dir /dev/shm = faster worker heartbeat (RAM-backed)
gunicorn \
    --workers 4 \
    --threads 16 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --bind 0.0.0.0:5000 \
    --access-logfile - \
    --error-logfile - \
    "app:create_app()"
