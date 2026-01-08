#!/usr/bin/env bash
# =============================================================
# NeoSpace Full Production Stack — Caddy + Gunicorn
# =============================================================
# Runs:
#   1. Gunicorn (Python backend) on port 5000
#   2. Caddy (reverse proxy) on ports 80/443
#
# Caddy handles: TLS, compression, static files, micro-caching
# Gunicorn handles: Flask app + SocketIO
# =============================================================

set -e
cd "$(dirname "$0")"

# Check for venv
if [ ! -f ".venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Please run: ./scripts/setup_venv.sh"
    exit 1
fi

# Check for Caddy
if ! command -v caddy &> /dev/null; then
    echo "Caddy not installed!"
    echo "Please run: sudo ./scripts/install_caddy.sh"
    exit 1
fi

source .venv/bin/activate

# Set Flask-SocketIO to threading mode
export SOCKETIO_ASYNC_MODE=threading

echo "========================================"
echo " NeoSpace Production Stack"
echo "========================================"
echo " Caddy: :80/:443 → Gunicorn :5000"
echo " Gunicorn: 4 workers × 16 threads"
echo "========================================"

# Start Gunicorn in background
gunicorn \
    --workers 4 \
    --threads 16 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --bind 127.0.0.1:5000 \
    --access-logfile - \
    --error-logfile - \
    --daemon \
    --pid /tmp/neospace_gunicorn.pid \
    "app:create_app()"

echo "Gunicorn started (PID: $(cat /tmp/neospace_gunicorn.pid))"

# Start Caddy in foreground (Ctrl+C to stop)
echo "Starting Caddy..."
caddy run --config Caddyfile

# On exit, kill Gunicorn
trap "kill $(cat /tmp/neospace_gunicorn.pid) 2>/dev/null" EXIT
