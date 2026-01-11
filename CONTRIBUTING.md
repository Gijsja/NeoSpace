# Contributing to NeoSpace

Welcome, and thank you for your interest in contributing to NeoSpace!

## Core Philosophies

1.  **Server Authority**: The backend is the source of truth. The frontend is a "dumb terminal" that renders HTML fragments sent via WebSockets.
2.  **No Build Step**: We use vanilla JS, CSS, and HTML. No Webpack, no React, no complex toolchains.
3.  **Neubrutalism**: Our UI design language is bold, high-contrast, and quirky. See `ui/css/input.css` for the design system.
4.  **Bolt ⚡**: We value performance and reliability.
    - Code should be instrumented for observability.
    - Database queries should be efficient (use indexes).
    - Tests must pass (`pytest`).

## Getting Started

1.  Clone the repository.
2.  Run `./scripts/setup_venv.sh` to set up your environment.
3.  Run `./startlocal.sh` to start the development server.

## PR Process

1.  Create a feature branch.
2.  Write code and **tests**.
3.  Run `pytest` to ensure no regressions.
4.  Submit a Pull Request using the template provided.

## Style Guide

- **Python**: PEP 8, 4 spaces indentation.
- **JavaScript/HTML/CSS**: 2 spaces indentation.
- **Design**: Stick to the Tailwind utility classes defined in our config.
