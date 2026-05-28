import asyncio
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Login
        print("Logging into Django Admin...")
        page.goto("http://localhost:8000/admin/login/")
        page.fill('input[name="username"]', 'admin@teraka.org')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_url("**/admin/")

        # 2. Dashboard
        print("Capturing Dashboard...")
        page.goto("http://localhost:8000/admin/")
        page.screenshot(path="verification_dashboard.png", full_page=True)

        # 3. User Roles List
        print("Capturing User Roles...")
        page.goto("http://localhost:8000/admin/core/userrole/")
        page.screenshot(path="verification_userroles.png", full_page=True)

        # 4. RBAC Hub
        print("Capturing RBAC Hub...")
        page.goto("http://localhost:8000/admin/rbac/")
        page.screenshot(path="verification_rbac_hub.png", full_page=True)

        browser.close()
        print("Screenshots saved.")

if __name__ == "__main__":
    run()
