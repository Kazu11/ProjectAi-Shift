from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:8080/manage")

    # Add a new employee
    page.fill("input[name=name]", "Alice")
    page.click("input[value='Add Employee']")

    # Verify the employee was added
    expect(page.locator("text=Alice")).to_be_visible()

    # Take a screenshot
    page.screenshot(path="manage_page_test.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
