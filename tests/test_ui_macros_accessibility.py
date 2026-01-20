import pytest
from flask import Flask, render_template_string
import os

def test_password_toggle_macro_accessibility():
    """
    Verify that the password input macro:
    1. Uses :type binding for toggling
    2. Has a toggle button with :aria-label
    3. Has focus-visible styles
    4. Does NOT have tabindex="-1" on the button
    """
    # Point Flask to the correct template folder (current directory)
    app = Flask(__name__, template_folder=os.path.abspath("templates"))

    # Minimal template using the macro
    template = """
    {% from "components/ui_macros.html" import input %}
    {{ input(name="password", type="password", label="Password") }}
    """

    with app.app_context():
        # Render the template
        rendered = render_template_string(template)

        # 1. Check for Alpine.js x-data on the wrapper
        assert 'x-data="{ show: false }"' in rendered, "Missing x-data for state management"

        # 2. Check for dynamic type binding
        assert ':type="show ? \'text\' : \'password\'"' in rendered, "Missing :type binding"

        # 3. Check for dynamic aria-label on the button
        assert ':aria-label="show ? \'Hide password\' : \'Show password\'"' in rendered, "Missing dynamic aria-label"

        # 4. Check for focus-visible styles
        assert 'focus-visible:ring-2' in rendered, "Missing focus-visible styles"

        # 5. Check that tabindex="-1" is NOT present on the button
        # We search specifically in the button tag part
        button_start = rendered.find('<button')
        button_end = rendered.find('</button>')
        button_html = rendered[button_start:button_end]

        assert 'tabindex="-1"' not in button_html, "Button should be keyboard accessible (no tabindex='-1')"
