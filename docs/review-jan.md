Below is a **handoff-ready Markdown document** intended to be given directly to **Claude (or another senior LLM / engineer)** to **execute the NeoSpace overhaul**.
It is explicit, prescriptive, and includes **concrete code examples**, target architecture, and refactoring guidance.

You can copy this verbatim into `NEOSPACE_HANDOFF.md`.

---

# NeoSpace — Handoff Architecture & Refactor Guide

**Audience:** Claude / Senior Engineer
**Purpose:** Execute a structured overhaul of the NeoSpace codebase
**Status:** Pre-Alpha → Stable v1 Refactor
**Core Philosophy:** Server-authoritative, WebSocket-first, minimal frontend logic

---

## 0. Project Intent (Read First)

NeoSpace is a **creative, real-time social platform** with these non-negotiable principles:

* The **server owns truth and state**
* WebSockets are a **primary transport**, not an afterthought
* Frontend JS is **thin**, rendering-focused only
* HTML fragments may be sent over WebSockets
* Avoid heavyweight frameworks where possible
* Prefer clarity, explicit contracts, and composability

The current codebase proves the concept but **compresses responsibilities**.
Your task is **not to rewrite**, but to **separate, formalize, and harden**.

---

## 1. Target Architecture (Authoritative)

You are expected to refactor toward the following structure:

```
neospace/
│
├── app/
│   ├── main.py              # app factory, startup
│   ├── config.py            # env loading
│   ├── lifecycle.py         # startup / shutdown hooks
│
├── core/
│   ├── security.py          # auth, password hashing
│   ├── permissions.py      # RBAC / permission model
│   ├── sessions.py
│   ├── rate_limit.py
│
├── domain/
│   ├── users/
│   │   ├── models.py
│   │   ├── service.py
│   │   └── repository.py
│   ├── messages/
│   ├── walls/
│   └── media/
│
├── services/
│   ├── auth_service.py
│   ├── message_service.py
│   ├── feed_service.py
│
├── api/
│   ├── http/
│   │   ├── auth_routes.py
│   │   └── page_routes.py
│   └── websocket/
│       ├── hub.py
│       └── handlers.py
│
├── db/
│   ├── engine.py
│   ├── models.py
│   ├── repositories/
│   └── migrations/
│
├── ui/
│   ├── templates/
│   └── js/
│
└── tests/
```

**Golden Rule:**
Routes orchestrate → Services decide → Repositories persist

---

## 2. Backend Architecture (What to Change)

### Problem (Current State)

* `app.py` mixes:

  * routing
  * auth
  * DB access
  * WebSocket logic
* Route handlers contain business rules
* Authorization is implicit and inconsistent

### Required Outcome

* Routes become **thin adapters**
* Business logic moves into services
* Authorization is explicit and centralized

---

## 3. Authentication & Security (MANDATORY)

### Authentication Service (Example)

```python
# services/auth_service.py
class AuthService:
    def authenticate(self, username: str, password: str) -> User:
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise AuthError("Invalid credentials")
        return user
```

### Password Hashing

* Use **argon2**
* Never handle raw passwords outside AuthService

```python
from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return ph.verify(hash, password)
```

---

## 4. Authorization & Permissions (REQUIRED)

### Permission Model

```python
# core/permissions.py
from enum import Enum

class Permission(str, Enum):
    READ_WALL = "read_wall"
    POST_MESSAGE = "post_message"
    ADMIN = "admin"
```

Attach permissions to users, **not routes**.

### Enforcement Example

```python
def require_permission(user, permission: Permission):
    if permission not in user.permissions:
        raise PermissionError()
```

All HTTP and WebSocket actions must call this.

---

## 5. Database Design & Repositories

### Problem

* SQL logic scattered in routes
* No abstraction
* High risk of N+1 queries

### Repository Pattern (Example)

```python
# domain/messages/repository.py
class MessageRepository:
    def get_feed(self, user_id: int, limit: int = 50):
        return (
            self.db.query(Message)
            .filter(Message.deleted_at.is_(None))
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
```

### Service Layer

```python
# domain/messages/service.py
class MessageService:
    def post_message(self, user, content: str):
        require_permission(user, Permission.POST_MESSAGE)
        return self.repo.create(user.id, content)
```

Routes **never** touch SQL.

---

## 6. WebSockets (STRICT CONTRACTS)

### Current Issue

* Message formats are implicit
* No versioning
* No authorization per message

### REQUIRED WebSocket Envelope

```json
{
  "v": 1,
  "type": "post_message",
  "data": {
    "content": "hello"
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

### WebSocket Handler Example

```python
def handle_ws_message(user, message):
    match message["type"]:
        case "post_message":
            require_permission(user, Permission.POST_MESSAGE)
            service.post_message(user, message["data"]["content"])
```

---

## 7. Frontend JS Rules (NON-NEGOTIABLE)

Frontend JS **may**:

* Render HTML
* Attach events
* Patch DOM

Frontend JS **may NOT**:

* Decide permissions
* Construct business rules
* Mutate state without server instruction

### Example Client Handler

```js
socket.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === "new_message") {
    document.querySelector("#feed").insertAdjacentHTML(
      "afterbegin",
      msg.payload.html
    );
  }
};
```

---

## 8. Templates

* Templates may assume **authorized, validated data**
* Never embed business logic
* Prefer partials for reusable UI

---

## 9. Deployment & Configuration

### Configuration Rules

* No secrets in code
* All config via environment variables
* `.env` for local only

```python
DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]
```

### Production Requirements

* Health check endpoint
* Structured logging
* Secure cookies
* Caddy or reverse proxy with headers

---

## 10. Testing Expectations

### Minimum Required Tests

#### Unit

* AuthService
* Permission enforcement
* MessageService

#### Integration

* Login flow
* WebSocket connect/send/receive
* Migration up/down

### Example Test

```python
def test_user_cannot_post_without_permission():
    with pytest.raises(PermissionError):
        service.post_message(user_without_perm, "hi")
```

---

## 11. Phased Execution Plan

### Phase 1 — Safety & Separation

* Split `app.py`
* Centralize auth
* Lock down WebSockets
* Repository abstraction

### Phase 2 — Formalization

* API + WS contracts
* Permissions everywhere
* Logging + error envelopes

### Phase 3 — Scale Readiness

* DB indices
* Caching
* Background tasks
* Horizontal WS strategy

---

## 12. Final Instruction to Claude

> You are expected to **refactor, not rewrite**.
> Preserve intent, reduce coupling, formalize contracts, and harden security.
> When in doubt, favor **explicitness over cleverness**.

---

### End of Handoff

