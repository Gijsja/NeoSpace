# 🐱 NeoSpace v0.5.8 🐱

[![CI](https://github.com/Gijsja/NeoSpace/actions/workflows/ci.yml/badge.svg)](https://github.com/Gijsja/NeoSpace/actions/workflows/ci.yml)
![Version](https://img.shields.io/badge/version-0.5.8-blue)
![Status](https://img.shields.io/badge/status-pre--alpha-orange)

> **Development Workspace / Unstable Snapshot**

NeoSpace is a server-authoritative, WebSocket-driven creative communication platform with customizable profile Walls and real-time chat.

**✨ Key Features**
- **Real-time Chat**: WebSocket-powered rooms with encrypted DMs.
- **Profile Walls**: MySpace-style customizable user pages with drag-and-drop stickers.
- **Creative Scripting**: In-browser coding sandbox (P5.js/Three.js) for user creations.
- **Cat Bots**: AI-driven NPC cats with personality and memory.
- **Observability**: Prometheus metrics and Admin Audit logs (v0.5.8).

**⚠️ Status: Pre-Alpha / Internal Sandbox**
This codebase is currently in active development. Features may be incomplete, and breaking changes happen frequently.

---

## 🚀 Quick Start

To run the application locally on Linux/Debian systems:

```bash
# 1. Setup the environment (first time only)
./scripts/setup_venv.sh

# 2. Start the server
./startlocal.sh
```

The application will be available at: [http://localhost:5000](http://localhost:5000)

---

## 📚 Documentation

Detailed documentation is located in the `docs/` directory.

- **[NeoSpace Documentation](docs/NEOSPACE.md)** — Architecture, Philosophy, Roadmap
- [UI Components](docs/ui_components.md)
- [Archive](docs/archive/) — Historical docs and sprint logs

---

## 🧪 Testing

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest
```

---

_This project follows a "Server Authority" architecture where the frontend is a dumb terminal receiving HTML fragments via WebSockets._
