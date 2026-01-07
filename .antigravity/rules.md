# NeoSpace Migration Rules (No-Build Edition)

> Immutable architectural rules. NO NODE.JS.

## 1. Sources of Truth

- **What are we building?** → Read `docs/BLUEPRINT.md`
- **How do we code it?** → Read `docs/PROTOCOL.md`
- **Everything else?** → Ignore `docs/archive/` unless specifically asked

## 2. The "No-Build" Tech Stack

| Layer       | Technology                       |
| ----------- | -------------------------------- |
| Core        | Python (Flask) serving templates |
| Reactivity  | Alpine.js (CDN)                  |
| Styling     | Tailwind CSS (CDN)               |
| Server Sync | HTMX                             |

**FORBIDDEN:** React, Vue, Webpack, Vite, `npm install`, `package.json`

## B. Component Strategy: "Macro Components"

Use Jinja2 template includes or inline `x-data` scopes:

```html
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>
  <div x-show="open">Content</div>
</div>
```

## C. The "Chesterton's Fence" Rule

- Do not delete legacy `routes/` logic
- Refactor View Layer (HTML), not Business Logic (Python)
- Keep Flask serving templates

## D. The E1/E2 Separation

| Layer  | Scope                     | Status    |
| ------ | ------------------------- | --------- |
| **E1** | Backend, DB, sockets      | 🛡️ Frozen |
| **E2** | UI, styling, interactions | 🔄 Active |
