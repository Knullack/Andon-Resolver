import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Use a relative import
from ..Code.andon_resolver import main

def start_andon_app():
    # Start the Andon Resolver App
    main(badge_number="your_badge_number", refresh_limit=1, head=True)

class TestAndonResolverApp(unittest.TestCase):
    def setUp(self):
        # Set up the Chrome WebDriver for testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode for testing
        self.driver = webdriver.Chrome(options=chrome_options)

    def tearDown(self):
        # Clean up resources after the test is executed
        self.driver.quit()

    def test_browser_window_opened(self):
        # Start the application in a separate process
        import multiprocessing
        app_process = multiprocessing.Process(target=start_andon_app)
        app_process.start()

        # Wait for the browser window to open (adjust the timeout as needed)
        WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/awsui-app-layout'))
        )

        # Assert that the browser window is open
        self.assertTrue(self.is_browser_window_opened())

        # Stop the application process
        app_process.terminate()

    def is_browser_window_opened(self):
        # Check if the browser window is open by inspecting the elements
        try:
            self.driver.find_element_by_xpath('/html/body/div/div/div/awsui-app-layout')
            return True
        except Exception:
            return False

if __name__ == '__main__':
    unittest.main()
