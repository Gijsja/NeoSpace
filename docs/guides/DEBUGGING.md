# Runbook: When Things Feel Weird

Debugging guide for LocalBBS.

---

## The Golden Rule

> **Assume the client is wrong.**

The server is the single source of truth. If state looks incorrect:

1. The client has stale data
2. The client missed an event
3. The client has a bug

It's _almost never_ the server.

---

## Diagnostic Steps

### Step 1: Check Socket Traffic

Open browser DevTools → Network → WS tab.

| Look For                 | Meaning                                 |
| ------------------------ | --------------------------------------- |
| No `message` events      | Client disconnected or missed broadcast |
| `backfill` with old data | Need to trigger fresh backfill          |
| No `connected` event     | WebSocket failed to initialize          |

### Step 2: Trigger Backfill

Force client to re-sync:

```javascript
socket.emit("request_backfill", { after_id: 0 });
```

### Step 3: Check Server Logs

```bash
# Run server in debug mode
python startlocal.py
```

Look for:

- SQL errors
- Uncaught exceptions
- Missing `g.user`

### Step 4: Restart Server

Nuclear option. Clears any stuck state.

```bash
pkill -f "python.*app"
python startlocal.py
```

---

## Quick Reference

| Symptom                | Likely Cause            | Fix                   |
| ---------------------- | ----------------------- | --------------------- |
| Messages not appearing | Missed broadcast        | Trigger backfill      |
| Wrong user on message  | `X-User` header missing | Check request headers |
| Edit/delete failing    | Not message owner       | Verify `g.user`       |
| 500 errors             | Database locked         | Restart server        |

---

See also: [CORE_INVARIANTS](CORE_INVARIANTS.md)
