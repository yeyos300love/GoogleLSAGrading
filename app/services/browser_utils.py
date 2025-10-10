from selenium import webdriver # pip install selenium webdriver-manager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os


def create_driver(headless=False):
    '''create chrome web driver instance based on envoirnment (local or replit)'''

    # Check if we're running in Replit
    if 'REPL_ID' in os.environ:
        replit_options = webdriver.ChromeOptions()
        replit_options.add_argument('--no-sandbox')
        if headless:
            replit_options.add_argument('--headless')
        replit_options.add_argument('--disable-dev-shm-usage')
        replit_options.add_argument('--window-size=1920,1080')  # Add window size
        replit_options.add_argument('--start-maximized')  # Add maximize
        
        # Use environment variables set in replit.nix
        chrome_binary = os.getenv('CHROME_BIN', '/usr/bin/chromium')
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
        
        replit_options.binary_location = chrome_binary
        service = Service(executable_path=chromedriver_path)
        
        driver = webdriver.Chrome(
            service=service,
            options=replit_options
        )
    else:
        # setup selenium
        options = Options()
        if headless:
            options.add_argument("--headless")  # run without opening a browser
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")  # Set a specific window size
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True) # keep browser open after script finishes

        chrome_service = Service()
        chrome_service.creation_flags = 0x08000000  # No Window flag for Windows
        driver = webdriver.Chrome(
            service=chrome_service,
            options=options
        )
    return driver


def wait_and_find_element(driver, by, value, timeout=40):
    '''wait for element to be clickable and return it'''
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    return element
