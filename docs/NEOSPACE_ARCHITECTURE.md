# NeoSpace: The "Juiced" Architecture

> **Directive for Claude:**
> This project is a **"No-Build" creative social platform**.
> We prioritize **raw performance and iteration speed** over enterprise abstraction.
> **Constraint:** Host hardware is a 2013 Mac (Dual Core, 8-16GB RAM) running Linux.
> **Philosophy:** No Docker containers. No Build steps. No "Clean Architecture" boilerplate.

---

## 1. The "Max Juice" Technology Stack

We use lightweight, high-performance components that minimize CPU overhead and maximize concurrency on older hardware.

| Layer             | Choice           | Rationale                                                                                               |
| :---------------- | :--------------- | :------------------------------------------------------------------------------------------------------ |
| **Reverse Proxy** | **Caddy**        | Replaces Nginx. Auto-HTTPS, Zstd compression, and 1-line micro-caching.                                 |
| **App Server**    | **Granian**      | Replaces Gunicorn/Gevent. Rust-based HTTP server. Handles WebSockets vastly better than Python workers. |
| **Framework**     | **Flask**        | Lightweight, proven. Paired with `Flask-SocketIO` for real-time state.                                  |
| **Database**      | **SQLite (WAL)** | Zero-latency, in-process DB. No network overhead. Tuned via PRAGMA.                                     |
| **Serialization** | **msgspec**      | Replaces Pydantic. 10-80x faster JSON serialization/validation.                                         |
| **Frontend**      | **Vanilla JS**   | HTML-over-WebSockets. No React, no Webpack, no `npm install`.                                           |

---

## 2. Database "God Mode" Configuration

**Crucial:** SQLite is the engine. It must be tuned to prevent blocking on the single-writer lock.

### The Connection Factory (`db.py`)

```python
import sqlite3
import msgspec
from flask import g

def get_db():
    if 'db' not in g:
        # TIMEOUT: 15s to allow clients to retry rather than hanging indefinitely
        g.db = sqlite3.connect('neospace.db', timeout=15)

        # --- THE JUICE CONFIG ---
        # 1. Concurrency: Writers do not block Readers
        g.db.execute('PRAGMA journal_mode = WAL;')

        # 2. Safety/Speed Balance: Sync less often (safe for social apps)
        g.db.execute('PRAGMA synchronous = NORMAL;')

        # 3. RAM Cache: Use 512MB RAM for cache (negative = kilobytes)
        g.db.execute('PRAGMA cache_size = -512000;')

        # 4. Memory Map: Map 2GB of DB file to RAM (Zero-copy reads)
        g.db.execute('PRAGMA mmap_size = 2147483648;')

        # 5. Temp Store: Sorts/Groups happen in RAM, not disk
        g.db.execute('PRAGMA temp_store = MEMORY;')

        # 6. Page Size: Must be 8192 (8KB) for modern SSD alignment
        # Requires "VACUUM;" run once manually.

        g.db.row_factory = sqlite3.Row
    return g.db
```

---

## 3. Server Configuration (Granian)

We reject Gevent (Async Python) because SQLite blocks it. We use **Granian (Rust)** which manages the event loop outside Python, or **Gunicorn with Threads**.

**The Run Command:**

```bash
# Granian (Preferred):
granian --interface wsgi --port 5000 --workers 4 --threads 2 app:app

# OR Gunicorn (Alternative):
gunicorn -w 4 --threads 16 --worker-class gthread --worker-tmp-dir /dev/shm app:app
```

---

## 4. The "Micro-Caching" Layer (Caddy)

We use Caddy to absorb "viral" read traffic. Requests for public feeds never hit Python if they were served recently.

**`Caddyfile` Configuration:**

```caddyfile
localhost {
    # Free Speed: Compress everything with Zstandard (faster than Gzip)
    encode zstd gzip

    # Static Assets: Bypass Python entirely
    handle /static/* {
        file_server
    }

    # Micro-Cache: Cache public reads for 1 second
    # This turns 1000 req/sec into 1 req/sec for the backend.
    @cacheable {
        method GET
        path /wall/* /directory /public-feed
    }
    header @cacheable Cache-Control "max-age=1"

    # Reverse Proxy
    reverse_proxy 127.0.0.1:5000 {
        header_up Host {host}
        header_up X-Real-IP {remote}
    }
}
```

---

## 5. Coding Patterns & "The Law"

### Law 1: Short Transactions (The "Prepare-Then-Commit" Pattern)

**NEVER** perform I/O (File writes, API calls, Sleep) inside a `with db:` block.

- **Bad:** `Open Tx -> Save File -> Insert Row -> Commit`
- **Good:** `Save File -> Open Tx -> Insert Row -> Commit`

### Law 2: No Over-Abstraction

- **Reject:** Repository Patterns, Abstract Base Classes, Clean Architecture Layers.
- **Accept:** Vertical Slices. Put the SQL query directly in the Route handler or a localized helper function. We need visibility, not abstraction.

### Law 3: Hybrid Caching

- **Public Data:** Relies on Caddy (HTTP Cache).
- **Private Data:** Relies on Python `lru_cache` or `Flask-Caching` (SimpleCache).
- **Do Not:** Install Redis unless absolutely necessary.

### Law 4: Validation Speed

Use `msgspec` for internal data structures and heavy JSON payloads. It is strictly faster than Pydantic.

```python
import msgspec

class Message(msgspec.Struct):
    id: int
    content: str
    timestamp: float

# decoding is instant
data = msgspec.json.decode(payload, type=Message)
```

---

## 6. Directory Structure (Optimized)

Keep related logic together. `mutations` and `queries` folders are good—keep them.

```text
NeoSpace/
├── app.py                 # App Factory
├── db.py                  # "God Mode" SQLite Connection
├── Caddyfile              # The Edge Server config
├── requirements.txt       # Keep it lean (Flask, Granian, msgspec, etc)
│
├── routes/                # HTTP Endpoints (Vertical Slices)
│   ├── wall.py
│   ├── chat.py
│   └── ...
│
├── mutations/             # Write Operations (Short Transaction Logic)
│   ├── post_mutations.py
│   └── ...
│
├── queries/               # Read Operations (Cached)
│   ├── feed_queries.py
│   └── ...
│
├── static/                # Raw Assets
├── templates/             # Jinja2
└── ui/                    # Vanilla JS Modules
```
