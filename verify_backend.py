
import asyncio
from playwright.async_api import async_playwright

async def verify_backend():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Login
        print("Navigating to login page...")
        await page.goto("http://localhost:8000/admin/login/")
        await page.fill('input[name="username"]', "admin@teraka.org")
        await page.fill('input[name="password"]', "admin")
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        # 2. Dashboard
        print("Capturing Dashboard...")
        await page.goto("http://localhost:8000/admin/dashboard/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="verify_dashboard.png", full_page=True)

        # 3. Users List
        print("Capturing Users list...")
        await page.goto("http://localhost:8000/admin/core/users/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="verify_users.png", full_page=True)

        # 4. Audit Log (assuming there is a view for it)
        print("Capturing Audit Logs...")
        await page.goto("http://localhost:8000/admin/core/auditlog/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="verify_audit.png", full_page=True)

        # 5. Members List (checking the data we added)
        print("Capturing Members list...")
        await page.goto("http://localhost:8000/admin/core/membre/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="verify_membres.png", full_page=True)

        await browser.close()
        print("Verification complete. Screenshots saved.")

if __name__ == "__main__":
    asyncio.run(verify_backend())
