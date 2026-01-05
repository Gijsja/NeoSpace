# API Reference

HTTP REST endpoints for LocalBBS.

> ⚠️ **Endpoint behavior is frozen in E2.** See [CORE_FROZEN](CORE_FROZEN.md).

---

## Authentication

Currently uses header-based pseudo-auth:

```
X-User: <username>
```

If omitted, defaults to `"anonymous"`.

---

## Endpoints

### `POST /send`

Create a new message.

**Request:**

```json
{
  "content": "Hello, world!"
}
```

**Response:**

```json
{
  "id": 123
}
```

**Notes:**

- Content is HTML-escaped before storage
- Broadcasts `message` event to all connected clients

---

### `POST /edit`

Edit an existing message.

**Request:**

```json
{
  "id": 123,
  "content": "Updated content"
}
```

**Response:**

```json
{
  "ok": true,
  "id": 123
}
```

**Errors:**

| Status | Reason                       |
| ------ | ---------------------------- |
| `400`  | Missing message `id`         |
| `403`  | Not message owner            |
| `404`  | Message not found or deleted |

---

### `POST /delete`

Soft-delete a message.

**Request:**

```json
{
  "id": 123
}
```

**Response:**

```json
{
  "ok": true,
  "id": 123
}
```

**Errors:**

| Status | Reason                               |
| ------ | ------------------------------------ |
| `400`  | Missing message `id`                 |
| `403`  | Not message owner                    |
| `404`  | Message not found or already deleted |

---

### `GET /backfill`

Retrieve all messages (HTTP fallback for WebSocket).

**Response:**

```json
{
  "messages": [{ "id": 1, "user": "alice", "content": "Hello" }]
}
```

---

### `GET /unread`

Get count of non-deleted messages.

**Response:**

```json
{
  "count": 42
}
```

---

## Error Response Format

All error responses include:

```json
{
  "ok": false,
  "error": "Human-readable error message"
}
```
