"""
Script to open Chrome, navigate to Google.sk, search for SAP official website,
navigate to sap.com, and take a screenshot when the page is loaded.

Requirements:
    pip install selenium webdriver-manager
"""

import subprocess
import sys

# Ensure webdriver-manager is installed
try:
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os


def setup_driver():
    """Set up Chrome WebDriver with proper options."""
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def handle_cookie_consent(driver):
    """Handle Google cookie consent dialog if it appears."""
    try:
        accept_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Accept') or contains(., 'Prijať') "
                "or contains(., 'Súhlasím') or contains(., 'Accept all') "
                "or contains(., 'Prijať všetko')]"))
        )
        accept_btn.click()
        time.sleep(2)
        print("  Cookie consent accepted.")
    except Exception:
        print("  No cookie consent dialog found or already dismissed.")


def search_google(driver, search_term):
    """Search for a term on Google."""
    # Find and use the search box
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.clear()
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    # Wait for page to load (use URL change as indicator)
    time.sleep(4)
    WebDriverWait(driver, 10).until(
        lambda d: "search" in d.current_url or "q=" in d.current_url
    )
    print(f"  Search completed for: '{search_term}'")
    print(f"  Current URL: {driver.current_url}")


def navigate_to_sap(driver):
    """Click on SAP official website link from search results."""
    try:
        # Try multiple XPath patterns to find SAP link
        sap_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "//a[contains(@href, 'www.sap.com')][1]"))
        )
        sap_link.click()
        print("  Clicked on SAP link from search results.")
    except Exception:
        print("  SAP link not found in results. Navigating directly to sap.com...")
        driver.get('https://www.sap.com')

    # Wait for SAP page to fully load
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(5)  # Additional wait for dynamic content to render
    print(f"  SAP page loaded. Current URL: {driver.current_url}")
    print(f"  Page title: {driver.title}")


def take_screenshot(driver, filename=None):
    """Take a screenshot and save it."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sap_official_web_screenshot_{timestamp}.png"

    screenshot_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(screenshot_dir, filename)

    result = driver.save_screenshot(screenshot_path)

    if result and os.path.exists(screenshot_path):
        file_size = os.path.getsize(screenshot_path)
        print(f"\n  {'='*50}")
        print(f"  Screenshot saved successfully!")
        print(f"  Location: {screenshot_path}")
        print(f"  File size: {file_size:,} bytes")
        print(f"  {'='*50}")
    else:
        print("  ERROR: Failed to save screenshot!")

    return screenshot_path


def main():
    """Main function to execute the screenshot workflow."""
    driver = None
    try:
        # Setup
        print("Starting Chrome browser...")
        driver = setup_driver()

        # Step 1: Navigate to Google.sk
        print("\nStep 1: Navigating to Google.sk...")
        driver.get('https://www.google.sk')
        time.sleep(3)

        # Step 2: Handle cookie consent
        print("\nStep 2: Handling cookie consent...")
        handle_cookie_consent(driver)

        # Step 3: Search for SAP official web
        print("\nStep 3: Searching for 'SAP official web'...")
        search_google(driver, "SAP official web")

        # Step 4: Navigate to SAP website
        print("\nStep 4: Navigating to SAP official website...")
        navigate_to_sap(driver)

        # Step 5: Take screenshot
        print("\nStep 5: Taking screenshot...")
        screenshot_path = take_screenshot(driver)

        return screenshot_path

    except Exception as e:
        print(f"\n  ERROR: {type(e).__name__}: {e}")
        if driver:
            # Take error screenshot for debugging
            error_path = take_screenshot(driver, "error_screenshot.png")
            print(f"  Error screenshot saved at: {error_path}")
        raise
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed. Done!")


if __name__ == "__main__":
    main()