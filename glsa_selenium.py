from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import sys
import os
from data import USERNAME, PASSWORD



# login
username = USERNAME
password = PASSWORD
# urls
LOGIN_URL = 'https://ads.google.com/localservices/'


# setup selenium
options = Options()
#options.add_argument("--headless")  # run without opening a browser
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")  # Set a specific window size
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

def create_driver():
    """Create a Chrome driver instance based on the environment"""
    global driver
    
    try:
        # Check if we're running in Replit
        if 'REPL_ID' in os.environ:
            replit_options = webdriver.ChromeOptions()
            replit_options.add_argument('--no-sandbox')
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
            chrome_service = Service()
            chrome_service.creation_flags = 0x08000000  # No Window flag for Windows
            driver = webdriver.Chrome(
                service=chrome_service,
                options=options
            )
            
    except Exception as e:
        print(f"Failed to create driver: {str(e)}")
        raise
    
    return driver

def wait_and_find_element(by, value, timeout=40):
    """Wait for element to be clickable and return it"""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    return element

if __name__ == '__main__':
    driver = create_driver()
    
    # podium.py '(971) 998-9211', '(509) 637-5941'

    examples = sys.argv[1:]

    driver.get(LOGIN_URL)

    #login_link = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/a')
    #login_link.send_keys(Keys.RETURN)

    login_button = wait_and_find_element(By.XPATH, '//*[@id="gb"]/div[2]/div[3]/div[1]/a')
    login_button.click()

    username_form = wait_and_find_element(By.XPATH, '//*[@id="identifierId"]')
    username_form.send_keys(username)
    #username_form.send_keys(Keys.RETURN)
    username_form_submit = wait_and_find_element(By.XPATH, '//*[@id="identifierNext"]/div/button')
    username_form_submit.click()

    password_form = wait_and_find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
    password_form.send_keys(password)
    password_form_submit = wait_and_find_element(By.XPATH, '//*[@id="passwordNext"]/div/button')
    #password_form_submit.click()

    # Advantage Heating & Air Conditioning
    # account_selector = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div[2]/div[1]/span[1]/a')
    # account_selector.click()
    
    # filter calls table properly
    # charge_status_dropdown = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/span')
    # charge_status_dropdown.click()
    # charged_leads = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[1]/div[1]/div[2]/div[2]/div[2]')
    # charged_leads.click()
    # time_dropdown = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[1]/div[1]/span/div/div[1]/div/div[1]/div/div[1]/input')
    # time_dropdown.click()
    # last_month_option = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[2]/div/div/span[3]')
    # last_month_option.click()
