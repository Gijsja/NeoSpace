#!/usr/bin/env bash
# =============================================================
# Install Caddy on Debian/Ubuntu
# =============================================================
# Run with: sudo ./scripts/install_caddy.sh
# =============================================================

set -e

echo "Installing Caddy..."

# Install prerequisites
apt-get update
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl

# Add Caddy GPG key
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

# Add Caddy apt repository
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

# Install Caddy
apt-get update
apt-get install -y caddy

echo "Caddy installed successfully!"
caddy version
