# Socket Contract

WebSocket event specifications for client-server communication.

> ⚠️ **Payload shapes are frozen in E2.** See [CORE_FROZEN](CORE_FROZEN.md).

---

## Client → Server Events

### `send_message`

Send a new message to the room.

```json
{
  "user": "string",
  "content": "string"
}
```

### `request_backfill`

Request message history.

```json
{
  "after_id": 0
}
```

| Field      | Type  | Description                                                     |
| ---------- | ----- | --------------------------------------------------------------- |
| `after_id` | `int` | Return messages with `id > after_id`. Use `0` for full history. |

---

## Server → Client Events

### `connected`

Sent on successful connection.

```json
{
  "ok": true
}
```

### `message`

Broadcast when a new message is created.

```json
{
  "id": 1,
  "user": "alice",
  "content": "Hello, world!",
  "deleted": false,
  "edited": false
}
```

### `backfill`

Response to `request_backfill`.

```json
{
  "phase": "continuity",
  "messages": [
    {
      "id": 1,
      "user": "alice",
      "content": "Hello",
      "deleted": false,
      "edited": false
    },
    {
      "id": 2,
      "user": "bob",
      "content": null,
      "deleted": true,
      "edited": false
    }
  ]
}
```

| Field      | Type     | Description                     |
| ---------- | -------- | ------------------------------- |
| `phase`    | `string` | Always `"continuity"`           |
| `messages` | `array`  | Ordered list of message objects |

---

## Message Object Schema

| Field     | Type             | Description                        |
| --------- | ---------------- | ---------------------------------- |
| `id`      | `int`            | Unique message identifier          |
| `user`    | `string`         | Username of sender                 |
| `content` | `string \| null` | Message text, `null` if deleted    |
| `deleted` | `bool`           | `true` if message was soft-deleted |
| `edited`  | `bool`           | `true` if message was edited       |
