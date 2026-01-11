from playwright.sync_api import sync_playwright

def verify_toast_a11y():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to login page...")
        page.goto("http://localhost:5000/")

        # Trigger a toast by failing login
        print("Attempting login with invalid credentials...")
        page.fill("input[name='username']", "invalid_user")
        page.fill("input[name='password']", "wrong_pass")
        page.click("button:has-text('Enter Grid')")

        # Wait for toast to appear
        try:
            toast_item = page.wait_for_selector("text=Access Denied", timeout=5000)
            print("Toast appeared.")
        except Exception:
            print("Toast did not appear. Verification failed.")
            exit(1)

        # Take screenshot of the toast
        page.screenshot(path="verification/verification.png")
        print("Screenshot saved to verification/verification.png")

        # 1. Verify Container Attributes
        container = page.locator(".fixed.bottom-6.right-6")

        role = container.get_attribute("role")
        aria_live = container.get_attribute("aria-live")

        print(f"Container Role: {role}")
        print(f"Container Aria-Live: {aria_live}")

        if role != "log":
            print("FAILURE: Container missing role='log'")
            exit(1)
        if aria_live != "polite":
            print("FAILURE: Container missing aria-live='polite'")
            exit(1)

        # 2. Verify Close Button Label
        toast_card = page.locator("div.border-2.border-black.shadow-\\[4px_4px_0_0_\\#000\\]", has_text="Access Denied").first

        close_btn = toast_card.locator("button:has(.ph-x)")
        btn_label = close_btn.get_attribute("aria-label")

        print(f"Close Button Label: {btn_label}")

        if btn_label != "Close notification":
            print("FAILURE: Close button missing aria-label='Close notification'")
            exit(1)

        print("SUCCESS: All accessibility attributes present.")
        browser.close()

if __name__ == "__main__":
    verify_toast_a11y()
