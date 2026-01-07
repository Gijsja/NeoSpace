# NeoSpace

> **Development Workspace / Unstable Snapshot**

NeoSpace is a server-authoritative, WebSocket-driven creative communication platform with customizable profile Walls and real-time chat.

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

- **[Start Here: Documentation Overview](docs/README.md)**
- [Roadmap & Backlog](docs/ROADMAP.md)
- [Architecture & Philosophy](docs/ARCHITECTURE.md)
- [Known Issues](docs/KNOWN_ISSUES.md)

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
