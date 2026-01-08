# Reactive Component System

This project uses **Alpine.js** and **Tailwind CSS** to create reusable, reactive UI components that mimic the functionality of libraries like shadcn/ui but fit our "No-Build" Flask architecture.

## Architecture

Components are implemented as **Jinja2 Macros** in `templates/components/`.
Each component handles its own:

- **HTML Structure**: Semantic markup.
- **Styling**: Tailwind CSS classes (using the "Neubrutalist" tokens).
- **Behavior**: Alpine.js `x-data` logic for state and interactivity.

## Installation

Ensure your base template includes Alpine.js and Tailwind CSS (or the output CSS file).

```html
<script
  defer
  src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"
></script>
```

## Available Components

### 1. Core Elements

**Button:**

```jinja
{% from "components/button.html" import button %}
{{ button('Click Me', variant='primary') }}
{{ button('Delete', variant='destructive', size='sm') }}
```

**Input:**

```jinja
{% from "components/input.html" import input %}
{{ input('email', 'Email Address', type='email', placeholder='name@example.com') }}
```

**Card:**

```jinja
{% from "components/card.html" import card %}
{% call card(title="Card Title", description="Subtitle here") %}
    Content goes here.
{% endcall %}
```

### 2. Overlays

**Dialog (Modal):**

```jinja
{% from "components/dialog.html" import dialog %}
{% call dialog('confirm-modal', 'Are you sure?', trigger_text="Open Modal") %}
    <p>This action cannot be undone.</p>
{% endcall %}
```

**Dropdown Menu:**

```jinja
{% from "components/dropdown.html" import dropdown, dropdown_item %}
{% call dropdown(label="Menu") %}
    {{ dropdown_item("Profile", href="/profile") }}
    {{ dropdown_item("Logout", href="/logout", destructive=True) }}
{% endcall %}
```

**Command Palette (CMD+K):**

```jinja
{% from "components/command.html" import command_palette %}
{{ command_palette() }}
<!-- Place once in base layout -->
```

### 3. Data Display

**Avatar:**

```jinja
{% from "components/avatar.html" import avatar %}
{{ avatar(src='url.jpg') }}
{{ avatar(text='JD') }} <!-- Fallback initials -->
```

**Badge:**

```jinja
{% from "components/badge.html" import badge %}
{{ badge('New', variant='acid') }}
```

**Skeleton:**

```jinja
{% from "components/skeleton.html" import skeleton %}
{{ skeleton('h-4 w-32') }}
```

### 4. Navigation & Media

**Switch (Toggle):**

```jinja
{% from "components/switch.html" import switch %}
{{ switch('airplane-mode', 'Airplane Mode', checked=True) }}
```

**Tabs:**

```jinja
{% from "components/tabs.html" import tabs, tab_panel %}
{% call tabs('my-tabs', [{'id': 'a', 'label': 'Tab A'}, {'id': 'b', 'label': 'Tab B'}]) %}
    {% call tab_panel('a') %} Content A {% endcall %}
    {% call tab_panel('b') %} Content B {% endcall %}
{% endcall %}
```

**Audio Player:**

```jinja
{% from "components/components/audio_player.html" import audio_player %}
{{ audio_player() }}
```

## Creating New Components

1. Create a new file in `templates/components/` (e.g., `rating.html`).
2. Define a macro: `{% macro rating(score) %} ... {% endmacro %}`.
3. Use Alpine `x-data` for any internal state.
4. Use Tailwind for all styling.
