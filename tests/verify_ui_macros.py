
import flask
from flask import Flask, render_template_string
import os
import sys

# Ensure we can import from the app root if needed, but for this simple test, just Flask is enough.
sys.path.append(os.getcwd())

def test_password_input_macro():
    # Use absolute path for template folder to be safe
    template_folder = os.path.join(os.getcwd(), 'templates')
    app = Flask(__name__, template_folder=template_folder)

    # Template string that imports the macro and uses it
    template_code = """
    {% from "components/ui_macros.html" import input %}
    {{ input('password', 'Password', type='password') }}
    """

    with app.app_context():
        try:
            rendered = render_template_string(template_code)

            print("Rendered HTML for password input:")
            print(rendered)

            # Check for bad state
            if 'tabindex="-1"' in rendered:
                print("\n[FAIL] tabindex='-1' STILL PRESENT.")
            else:
                print("\n[PASS] tabindex='-1' successfully removed.")

            # Check for good state
            if ':aria-label' in rendered:
                 print("[PASS] :aria-label binding found.")
            else:
                 print("[FAIL] :aria-label binding MISSING.")

            if 'focus-visible:ring' in rendered:
                 print("[PASS] focus-visible styles found.")
            else:
                 print("[FAIL] focus-visible styles MISSING.")

        except Exception as e:
            print(f"Error rendering template: {e}")
            raise

if __name__ == "__main__":
    test_password_input_macro()
