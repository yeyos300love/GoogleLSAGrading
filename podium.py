from selenium import webdriver # pip install selenium webdriver-manager
from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
#import pickle
import time 
import sys
import os
import json
import tempfile
#from bs4 import BeautifulSoup
from data import USERNAME, PASSWORD



# login
username = USERNAME
password = PASSWORD
# urls
#TRANSCRIPTS_URL = 'https://app.podium.com/phones/calls?locationUid=60ace1e3-950b-59d4-9b46-8ffe543e9848&phoneNumber=%2B1' + str(phone_num) + '&viewAllLocations=false'  
#CALLS_URL = 'https://app.podium.com/phones/calls'
LOGIN_URL = 'https://auth.podium.com/'


# setup selenium
options = Options()
options.add_argument("--headless")  # run without opening a browser
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")  # Set a specific window size
options.add_argument("--start-maximized")
#options.add_experimental_option("detach", True) # keep browser open after script finishes

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

def login(url: str):
    driver.get(url)

    user_box = wait_and_find_element(By.XPATH, '//*[@id="emailOrPhoneInput"]')
    user_box.clear()
    user_box.send_keys(username)
    user_box.send_keys(Keys.RETURN)
    time.sleep(2)  # increased wait time

    pass_box = wait_and_find_element(By.XPATH, '//*[@id="passwordInput"]')
    pass_box.clear()
    pass_box.send_keys(password)
    pass_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # Print prompt and flush to ensure it's sent to stdout
    print('Enter temporary code: ', end='', flush=True)
    two_fact = input().strip()
    
    two_fact_box = driver.find_element(By.XPATH, '//*[@id="verificationCode"]')
    two_fact_box.send_keys(two_fact)
    two_fact_box.send_keys(Keys.RETURN)
    time.sleep(5) # wait for the page to load





def search_number(phone_num: str):
    search_box = wait_and_find_element(By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input')
    search_box.clear()
    search_box.click()
    time.sleep(1)
    search_box.send_keys(phone_num)
    time.sleep(1)
    search_box.send_keys(Keys.RETURN)

    try:
        # select first call
        hover_call_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app-content-area"]/div/div/div[2]/div/div[2]/div/div[1]/div/div[3]/div[2]'))
        )
        hover_call_box.click()
    except:
        transcript_text = ['FAILED', 'No call box', 'No conversations found in Podium']

    try:
        # get transcript
        transcript_pane = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app-container"]/div[5]/div/div[2]/div[2]/div/div[2]'))
        )
        
        # store transcript text
        transcript_text = transcript_pane.text.split('\n')[2:]
    except:
        transcript_text = ['FAILED', 'No transcript text', 'Ensure call box selected is the correct one']
    
    # clear the search box
    #search_box = wait_and_find_element(By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input')
    search_box.click()
    search_box.send_keys(Keys.CONTROL + 'a')
    search_box.send_keys(Keys.DELETE)
    time.sleep(1)
    
    return transcript_text

def navigate_to_transcript(phone_nums: list) -> list:
    # add mobile number pop up - wait for it to be clickable
    try:
        pop_up_cancel = wait_and_find_element(By.XPATH, '//*[@id="chakra-modal-2"]/button')
        pop_up_cancel.click()
    except:
        print("No popup found, continuing...")

    # select calls button on left side navigation bar
    call_nav_button = wait_and_find_element(By.XPATH, '//*[@id="navigate-to-phones"]')
    call_nav_button.click()

    # missed, all calls, etc.
    # button xpath changed on every broswer instance, selected surrounding button
    option_dropdown = wait_and_find_element(By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[2]')
    option_dropdown.click()
    # full xpath needed for option since name was tied to changing button
    all_calls_option = wait_and_find_element(By.XPATH, '/html/body/div[1]/div[2]/div[4]/div/div/div[1]/div[1]/div/div[3]/div/button[1]')
    all_calls_option.click()

    #transcripts_element_text = {}
    for i, num in enumerate(phone_nums, 1):
        print(f"FETCH_PROGRESS: {i}/{len(phone_nums)}", flush=True)
        
        progress_file = 'data/uploaded_09JUN2025.json'

        raw_transcript = search_number(num)

        # remove '•' & convo letter icon
        transcript_list = [item for item in raw_transcript if len(item) > 1]
        # group data as [name, time, text]
        transcript = [transcript_list[i:i+3] for i in range(0, len(transcript_list), 3)]
        transcript_str = "\n\n".join(f"{i[0]} • {i[1]}\n{i[2]}" for i in transcript) #string

        save_progress(num, transcript_str, progress_file)

        #transcripts_element_text[num] = search_number(num)
        #print(num, transcripts_element_text[num])

    #return transcripts_element_text


def save_progress(phone_num, transcript_data, progress_file):
    """Save individual transcript progress to file"""
    try:
        # Load existing progress
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
        else:
            progress = []
        
        # Find existing entry with the same customer phone number
        existing_entry = None
        for entry in progress:
            if entry.get("customer") == phone_num:
                existing_entry = entry
                break
        
        if existing_entry:
            # Update existing entry's transcript
            existing_entry["transcript"] = transcript_data
        else:
            # Create new transcript object if no existing entry found
            transcript_obj = {
                "customer": phone_num,
                "transcript": transcript_data,
                "grade": "",
                "grade_secondary": ""
            }
            progress.append(transcript_obj)
        
        # Save updated progress
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"ERROR_SAVING: {phone_num} - {str(e)}", flush=True)
        return False


if __name__ == '__main__':
    
    # customer_phones_list = sys.argv[1:-1] # remove python, podium.py, & closing ]
    # customer_phones_list[0] = customer_phones_list[0][1:] # remove opening [
    #print(customer_phones_list)
    #for customer_phone in customer_phones_list:
        #print(customer_phone)

    json_file = sys.argv[1:][0]
    PATH = os.path.join(os.path.dirname(__file__), 'data', json_file)

    # Load existing progress
    if os.path.exists(PATH):
        with open(PATH, 'r', encoding='utf-8') as f:
            customer_data = json.load(f)

    # Extract all customer phone numbers
    customer_phones_list = [entry["customer"] for entry in customer_data]

    driver = create_driver()

    login(LOGIN_URL)
    transcripts_raw = navigate_to_transcript(customer_phones_list)
    #print(transcripts_raw)

    # close browser session
    driver.quit()
    

##### CTRL + / #####
