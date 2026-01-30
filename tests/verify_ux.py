from flask import Flask, render_template_string


def create_test_app():
    app = Flask(__name__, template_folder='../templates')
    return app


def verify_password_input_accessibility():
    app = create_test_app()
    with app.app_context():
        # Render the macro
        template = """
        {% from "components/ui_macros.html" import input %}
        {{ input('password', 'Password', type='password',
           placeholder='••••••••', attrs='x-model="password" required') }}
        """
        output = render_template_string(template)

        # Checks
        print("Checking output for accessibility improvements...")

        if 'tabindex="-1"' in output:
            print("❌ FAILURE: tabindex='-1' found on button")
        else:
            print("✅ SUCCESS: tabindex='-1' removed")

        if 'aria-label' in output:
            print("✅ SUCCESS: aria-label found")
        else:
            print("❌ FAILURE: aria-label NOT found on password toggle button")

        if 'focus-visible:ring' in output or 'focus:ring' in output:
            print("✅ SUCCESS: focus ring class found")
        else:
            print("❌ FAILURE: Focus ring class NOT found")

        # Check for dynamic label
        expected_label = ":aria-label=\"show ? 'Hide password' : " \
                         "'Show password'\""
        if expected_label in output:
            print("✅ SUCCESS: Dynamic aria-label found")
        else:
            print("❌ FAILURE: Dynamic aria-label pattern not found.")


if __name__ == "__main__":
    verify_password_input_accessibility()
