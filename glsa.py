from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserSession
from dotenv import load_dotenv
load_dotenv()

import asyncio
import sys
import os
import time
import json

from data import USERNAME, PASSWORD
from data import convert_grade_secondary_to_index#, convert_grade_secondary_to_full


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
#options.add_experimental_option("detach", True)
options.add_argument("--remote-debugging-port=8080")


def create_driver():
    """Create a Chrome driver instance based on the environment"""
    global driver
    
    try:
        # Check if we're running in Replit
        if 'REPL_ID' in os.environ:
            replit_options = webdriver.ChromeOptions()
            replit_options.add_argument('--no-sandbox')
            #replit_options.add_argument('--headless')
            replit_options.add_argument('--disable-dev-shm-usage')
            replit_options.add_argument('--window-size=1920,1080')  # Add window size
            replit_options.add_argument('--start-maximized')  # Add maximize
            replit_options.add_argument("--remote-debugging-port=9223")
            
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


def grade_call(customer, grade, grade_secondary_short):
    print(f"Grading {customer} with grade {grade} and grade_secondary {grade_secondary_short}")

    grade_secondary_index = convert_grade_secondary_to_index(grade_secondary_short)

    rate_lead_button = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[2]/span/div[2]/div/div/div[1]/div[2]/div/button/span')
    time.sleep(1)
    rate_lead_button.click()

    # switch driver to iframe
    iframe = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'google-hats-survey_parent-dialog-dom'))
    )
    driver.switch_to.frame(iframe)

    if grade == 'Neither satisfied nor dissatisfied':
        nor_option = wait_and_find_element(By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[3]/div/button/div[2]')
        nor_option.click()

        # switch driver to back original
        driver.switch_to.default_content()

        done_survey_element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button')
        done_survey_element.click()  
        time.sleep(2)
        archive_option = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[1]/span/span')
        archive_option.click()
        time.sleep(1)

    elif grade == 'Very satisfied' and grade_secondary_short == 'Booked':
        satisfied_option = wait_and_find_element(By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[1]/div/button/div[2]')
        satisfied_option.click()

        converted_secondary_option = wait_and_find_element(By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[1]/sc-survey-single-select-button[1]/div')
        converted_secondary_option.click()

        # switch driver to back original
        driver.switch_to.default_content()

        done_survey_element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button')
        done_survey_element.click()  
        time.sleep(2)
        marked_booked_option = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[2]/span/span')
        marked_booked_option.click()
        time.sleep(1)
        save_survey_option = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div/div[2]/div[3]/div[2]/span/span')
        save_survey_option.click()
        time.sleep(1)

    elif grade == 'Very satisfied' and grade_secondary_short != 'Booked':
        satisfied_option = wait_and_find_element(By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[1]/div/button/div[2]')
        satisfied_option.click()

        grade_secondary_option = wait_and_find_element(By.XPATH, f'/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[1]/sc-survey-single-select-button[{grade_secondary_index}]/div')
        grade_secondary_option.click()
        #"Other" Positive Option
        #/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[2]/div/sc-survey-survey-custom-response/div/label/input

        # switch driver to back original
        driver.switch_to.default_content()

        done_survey_element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button')
        done_survey_element.click()  
        time.sleep(2)
        archive_option = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[1]/span/span')
        archive_option.click()
        time.sleep(1)

    elif grade == 'Very dissatisfied':
        dissatisfied_option = wait_and_find_element(By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[5]/div/button/div[2]')
        dissatisfied_option.click()

        grade_secondary_option = wait_and_find_element(By.XPATH, f'/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[1]/sc-survey-single-select-button[{grade_secondary_index}]/div')
        grade_secondary_option.click()

        # switch driver to back original
        driver.switch_to.default_content()

        done_survey_element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button')
        done_survey_element.click()       
        time.sleep(2)
        archive_option = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[1]/span/span')
        archive_option.click()
        time.sleep(1)
        
    else:
        raise ValueError(f"Invalid grade: {grade}")


def login(url: str):
    driver.get(url)

    #login_link = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/a')
    #login_link.send_keys(Keys.RETURN)

    login_button = wait_and_find_element(By.XPATH, '//*[@id="gb"]/div[2]/div[3]/div[1]/a')
    login_button.click()

    username_form = wait_and_find_element(By.XPATH, '//*[@id="identifierId"]')
    username_form.send_keys(username)
    #username_form.send_keys(Keys.RETURN)
    username_form_submit = wait_and_find_element(By.XPATH, '//*[@id="identifierNext"]/div/button')
    username_form_submit.click()

    password_form = wait_and_find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input', timeout=120)
    password_form.send_keys(password)
    password_form_submit = wait_and_find_element(By.XPATH, '//*[@id="passwordNext"]/div/button')
    password_form_submit.click()

    # # your organization will manage this profile
    # # select color
    # try:
    #     time.sleep(40)
    #     # Click Continue button
    #     ActionChains(driver).move_by_offset(776, 427).click().perform()
    #     print('click attempted')
    #     time.sleep(3)
    #     # Click Done button
    #     ActionChains(driver).move_by_offset(807, 468).click().perform()
    #     print('click attempted')
    #     time.sleep(3)
    # except:
    #     print("No Popup Found")


def get_final_index(n: int) -> int:
    remainder = n % 20
    #return 20 if remainder == 0 else remainder
    return 19 if remainder == 0 else remainder - 1


def calculate_clicks_to_last_page(n):
    """
    Calculate the number of clicks required to navigate to the last page
    of a paginated table.
    
    Args:
        n (int): Total number of rows
        
    Returns:
        int: Number of clicks needed to reach the last page
        
    Examples:
        >>> calculate_clicks_to_last_page(51)
        2
        >>> calculate_clicks_to_last_page(20)
        0
        >>> calculate_clicks_to_last_page(21)
        1
        >>> calculate_clicks_to_last_page(100)
        4
    """
    if n <= 0:
        return 0
    # Calculate total number of pages (ceiling division)
    total_pages = (n + 19) // 20  # equivalent to math.ceil(n / 20)
    # Number of clicks = total pages - 1 (since we start on page 1)
    clicks = total_pages - 1
    return clicks


async def run_agent():
    """Run the browser-use agent"""
    llm = ChatOpenAI(model="gpt-4.1")

    prompt = f'''
    1. You are setting the custom date range from {start_date} to {end_date}. The calendar popup is already open
    2. Set start date first to: {start_date} by:
        - Set correct month, use pagnation buttons of calendar popup to navigate to the correct month if necessary.
        - Click on the correct day
    3. Next, set end date to: {end_date} by:
        - Set correct month, use pagnation buttons of calendar popup to navigate to the correct month if necessary.
        - Click on the correct day
    4. STOP ALL ACTIONS
    '''
    
    # Configure browser session to connect to existing browser
    if 'REPL_ID' in os.environ:
        os.environ['CHROMIUM_FLAGS'] = '--no-sandbox --disable-setuid-sandbox --disable-seccomp-filter-sandbox'
        browser_session = BrowserSession(
            headless=False,
            debug_port=9223,
            cdp_url="http://localhost:9223",
            connect_to_existing_browser=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox", 
                "--disable-seccomp-filter-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--remote-debugging-port=9223",
                "--display=:0"
            ],
            executable_path=os.getenv('CHROME_BIN', '/nix/store/*/chromium/bin/chromium')
        )

    agent = Agent(
        task=prompt,
        llm=llm,
        browser_session=browser_session
    )

    result = await agent.run()
    return result




if __name__ == '__main__':
    args = sys.argv[1:]
    
    json_file = args[0]
    start_date = args[1]
    end_date = args[2]

    #print(f"start_date: {start_date}", flush=True)
    #print(f"end_date: {end_date}", flush=True)
    #print(f"json_file: {json_file}", flush=True)

    PATH = os.path.join(os.path.dirname(__file__), 'data', json_file)
    #PATH = os.path.join(os.path.dirname(__file__), 'sample_data', json_file)

    # Load existing progress
    if os.path.exists(PATH):
        with open(PATH, 'r', encoding='utf-8') as f:
            customer_data = json.load(f)          
    
            total_json_customers = len(customer_data) if 'customer_data' in locals() else 0
            print(f"Total JSON customers: {total_json_customers}")

    driver = create_driver()
    driver.maximize_window()
    
    login(LOGIN_URL)

    # Prompt user to continue
    print('perform 2fa')
    #print('hit cancel')
    input("hit enter to continue: ")

    # Advantage Heating & Air Conditioning
    account_selector = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/c-wiz/div/div[2]/div[2]/div[1]/span[1]/a')
    account_selector.click()
    time.sleep(1)
    # filter calls table by charged leads
    charge_status_dropdown = wait_and_find_element(By.CSS_SELECTOR, '[role="listbox"][aria-label="Charge phase filter"]')
    charge_status_dropdown.click()
    time.sleep(1)
    charged_leads = wait_and_find_element(By.CSS_SELECTOR, 'div[role="option"][data-value="Charged leads"]')
    charged_leads.click()
    time.sleep(1)
    # filter calls table by phone leads
    lead_status_dropdown = wait_and_find_element(By.CSS_SELECTOR, '[role="listbox"][aria-label="Lead type filter"]')
    lead_status_dropdown.click()
    time.sleep(1)
    phone_leads = wait_and_find_element(By.CSS_SELECTOR, 'div[role="option"][data-value="phone"]')
    phone_leads.click()
    time.sleep(1)
    # filter calls table
    time_dropdown = wait_and_find_element(By.CSS_SELECTOR, 'span.A37UZe.sxyYjd.MQL3Ob')
    time_dropdown.click()
    time.sleep(1)
    # filter calls table by last month
    if start_date == end_date:
        last_month_option = wait_and_find_element(By.CSS_SELECTOR, 'div[data-value="last_month"]')
        last_month_option.click()
        time.sleep(1)
        # filter calls table by custom range
    elif start_date != end_date:
        custom_range_option = wait_and_find_element(By.CSS_SELECTOR, 'div[data-value="custom"]')
        custom_range_option.click()
        result = asyncio.run(run_agent())
        apply_date_range_button = wait_and_find_element(By.CSS_SELECTOR, '[role="button"][aria-label="Apply"]')
        apply_date_range_button.click()

    # navigate to final page
    clicks_needed = calculate_clicks_to_last_page(total_json_customers)

    for i in range(clicks_needed):
        #next_button = WebDriverWait(driver, 5).until(
        #    EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[2]/c-wiz/div/span[2]/span[3]/span'))
        #)
        next_button = wait_and_find_element(By.CSS_SELECTOR, 'span[data-paginate="next"]')
        next_button.click()
        #print(f"Clicked next button {i + 1}/{clicks_needed}")
        time.sleep(2)  # Wait for page to load
    #print("Navigation to last page completed")
    
    #ex) 101-108 of 108
    #customer_frontend_element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[2]/c-wiz/div/span[2]/span[1]')
    #string_frontend_customers = customer_frontend_element.text
    #total_frontend_customers = int(string_frontend_customers.split()[-1])
    
    # Check if frontend and JSON customer counts match
    #if total_frontend_customers > total_json_customers:
    #    raise ValueError(f"Mismatch in customer counts: Frontend has {total_frontend_customers} customers, but JSON has {total_json_customers} customers")

    # Wait for element to be located and get its text
    #element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[8]/td[1]/div')
    
    #//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[7]
    #//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[8]
    #current_text = element.text
    #print(current_text)

    
    print('Begin Filling Forms')
    # Grading loop
    first_text = None
    cnt = 0 # customer count
    final_index = get_final_index(total_json_customers)

    while True:
        # Wait for element to be located and get its text
        #element = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[20]/td[1]/div/span') 
        #element = wait_and_find_element(By.XPATH, f'//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[{final_index}]/td[1]/div/span') 
        element = wait_and_find_element(By.CSS_SELECTOR, f'tr[data-row-id="{final_index}"]')
        current_text = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[3]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[11]/td[1]/div/span').text
        element.click()
        
        #print(element.text)
        
        #import random
        #current_text = random.choice(customer_data)['customer'] if customer_data else '(317) 956-0147'
        
        # Set first_text on first iteration
        if first_text is None:
            first_text = current_text
        # Stop if we've cycled back to the first text
        # Break only when all customers have been graded
        elif current_text == first_text and cnt+1 == total_json_customers:
            print(f"Cycled back to {current_text}")
            break
            
        # Find matching customer in customer_data
        grade = None
        grade_secondary = None
        for customer in customer_data:
            if customer.get('customer') == current_text:
                grade = customer.get('grade')
                grade_secondary = customer.get('grade_secondary')
                break
        
        # perform grading
        grade_call(current_text, grade, grade_secondary)
        cnt += 1
        print(f"{cnt}. GRADING_COMPLETE: {current_text}")
        
        # Wait for back button and click
        time.sleep(1)
        back_button = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[1]/div/span/span/span')
        time.sleep(1)
        back_button.click()
        #wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[1]/div/span/span/span').click()
        time.sleep(2)

    print('End Filling Forms')
    # close browser session
    driver.quit()
    


# audio tag when customer phone is clicked
#'//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[2]/span/div[2]/div/div/div[1]/div[2]/div/button/span'
#'<source src="https://ads.google.com/localservicesads/attachment/CODYlXkQh-DYkwwYheS0ZjIDZ2hzOAE?authuser=0" type="audio/mpeg">'