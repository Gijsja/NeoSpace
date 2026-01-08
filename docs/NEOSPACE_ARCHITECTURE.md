# NeoSpace: The "Juiced" Architecture

> **Directive for AI Assistants:**
> This project is a **"No-Build" creative social platform**.
> We prioritize **raw performance and iteration speed** over enterprise abstraction.
> **Constraint:** Host hardware is a 2013 Mac (Dual Core, 8-16GB RAM) running Linux.
> **Philosophy:** No Docker containers. No Build steps. No "Clean Architecture" boilerplate.

---

## 1. The "Max Juice" Technology Stack

| Layer             | Choice               | Rationale                                                    |
| :---------------- | :------------------- | :----------------------------------------------------------- |
| **Reverse Proxy** | **Caddy**            | Auto-HTTPS, Zstd compression, micro-caching                  |
| **App Server**    | **Gunicorn gthread** | Thread-based workers; SQLite-friendly, Flask-SocketIO compat |
| **Framework**     | **Flask**            | Lightweight, paired with `Flask-SocketIO` for real-time      |
| **Database**      | **SQLite (WAL)**     | Zero-latency, in-process. Tuned via PRAGMA                   |
| **Serialization** | **msgspec**          | 10-80x faster than Pydantic (Phase 4: lazy adoption)         |
| **Frontend**      | **Vanilla JS**       | HTML-over-WebSockets. No React, no Webpack                   |

---

## 2. Database "God Mode" Configuration

```python
# db.py - Connection Settings
db = sqlite3.connect('app.db', timeout=15)  # 15s retry window

# THE JUICE CONFIG
db.execute('PRAGMA journal_mode = WAL;')           # Readers don't block writers
db.execute('PRAGMA synchronous = NORMAL;')         # Balanced durability
db.execute('PRAGMA cache_size = -512000;')         # 512MB RAM cache
db.execute('PRAGMA mmap_size = 2147483648;')       # 2GB memory-mapped I/O
db.execute('PRAGMA temp_store = MEMORY;')          # Sorts in RAM
# Run once: PRAGMA page_size=8192; VACUUM;         # SSD alignment
```

---

## 3. Server Configuration

```bash
# Production: startprod.sh or startstack.sh
gunicorn -w 4 --threads 16 --worker-class gthread \
    --worker-tmp-dir /dev/shm --bind 0.0.0.0:5000 "app:create_app()"
```

| Setting      | Value    | Rationale                          |
| ------------ | -------- | ---------------------------------- |
| Workers      | 4        | One per core (2013 dual-core + HT) |
| Threads      | 16       | ~64 concurrent requests            |
| Worker class | gthread  | SQLite-compatible threading        |
| Tmp dir      | /dev/shm | RAM-backed heartbeat               |

---

## 4. The Caddy Layer

```caddyfile
:80 {
    encode zstd gzip                              # Compression
    handle /static/* { file_server }              # Bypass Python
    @cacheable { method GET; path /wall/* }
    header @cacheable Cache-Control "max-age=1"   # Micro-cache
    reverse_proxy 127.0.0.1:5000                  # Flask backend
}
```

---

## 5. The Laws

### Law 1: Short Transactions

Never perform I/O inside `with db:`. Prepare files first, then commit.

### Law 2: No Over-Abstraction

Reject Repository/Clean Architecture patterns. Use vertical slices.

### Law 3: Hybrid Caching

- Public data → Caddy (HTTP cache)
- Private data → Python `lru_cache`
- No Redis unless necessary

### Law 4: msgspec for Speed

Use `msgspec.Struct` for hot-path JSON (Phase 4 sprint item).

---

## 6. Startup Scripts

| Script          | Purpose                          |
| --------------- | -------------------------------- |
| `startlocal.sh` | Dev mode with Flask debug server |
| `startprod.sh`  | Gunicorn gthread (no Caddy)      |
| `startstack.sh` | Full stack: Caddy + Gunicorn     |

---

## 7. Sprint Backlog: Phase 4 (msgspec)

Lazy adoption — apply as files are touched:

- [ ] `mutations/message_mutations.py` — Message struct
- [ ] `queries/backfill.py` — Backfill response
- [ ] `routes/wall.py` — Wall post payloads
- [ ] `sockets.py` — Socket event payloads
