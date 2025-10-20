import unittest
from playwright.sync_api import sync_playwright, expect
import threading
import time
from app import app

class TestManagePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8080})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1) # Give the server a moment to start

    def test_add_employee(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://127.0.0.1:8080/manage")

            # Add a new employee
            page.fill("input[name=name]", "Playwright Test")
            page.click("input[value='Add Employee']")

            # Verify the employee was added
            expect(page.locator("text=Playwright Test")).to_be_visible()

            # Take a screenshot
            page.screenshot(path="manage_page_test.png")

            browser.close()

if __name__ == "__main__":
    unittest.main()
