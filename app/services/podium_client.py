from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from app.services.browser_utils import create_driver, wait_and_find_element
from flask import current_app
import time


def start_podium_subprocess():
    driver = create_driver()
    driver.get(current_app.config['PODIUM_URL'])

    # login
    wait_and_find_element(driver, By.XPATH, '//*[@id="emailOrPhoneInput"]').send_keys(current_app.config['USERNAME'])
    wait_and_find_element(driver, By.XPATH, '//*[@id="emailOrPhoneInput"]').send_keys(Keys.RETURN)
    time.sleep(2)
    wait_and_find_element(driver, By.XPATH, '//*[@id="passwordInput"]').send_keys(current_app.config['PASSWORD'])
    wait_and_find_element(driver, By.XPATH, '//*[@id="passwordInput"]').send_keys(Keys.RETURN)

    return driver

def perform_verification(driver, two_factor_code):
    wait_and_find_element(driver, By.XPATH, '//*[@id="verificationCode"]').send_keys(two_factor_code)
    wait_and_find_element(driver, By.XPATH, '//*[@id="verificationCode"]').send_keys(Keys.RETURN)
    time.sleep(5)

def continue_podium_subprocess(driver):
    try:
        wait_and_find_element(driver, By.XPATH, '//*[@id="chakra-modal-2"]/button').click()
    except:
        print('No popup found')

    # click calls navigation button
    wait_and_find_element(driver, By.XPATH, '//*[@id="navigate-to-phones"]').click()
    # option dropdown
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[2]').click()
    # select all calls
    wait_and_find_element(driver, By.XPATH, '/html/body/div[1]/div[2]/div[4]/div/div/div[1]/div[1]/div/div[3]/div/button[1]').click()

def search_number(driver, num: str):
    # remove any input in search box
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').clear()
    # select search box
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').click()
    time.sleep(1)
    # enter number in search box
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').send_keys(num)
    time.sleep(3)
    # press enter
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').send_keys(Keys.RETURN)
    time.sleep(4)

    try:
        # select first call
        wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[2]/div/div/div/div[1]/div/div[3]').click()
        try:
            # get transcript
            transcript_list =WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app-container"]/div[5]/div/div[2]/div[2]/div/div[2]/div[2]'))
            ).text.split('\n')[2:]
            if not transcript_text or all(not line.strip() for line in transcript_text):
                transcript_text = ['FAILED', 'No content', 'Check call box to see why it is blank.']
        except:
            transcript_list = ['FAILED', 'No transcript text', 'Ensure call box selected is the correct one.']
    except:
        transcript_list = ['FAILED', 'No call box', 'No conversations found in Podium.']

    # clear search box
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').click()
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').send_keys(Keys.CONTROL + 'a')
    wait_and_find_element(driver, By.XPATH, '//*[@id="app-content-area"]/div/div/div[1]/div[1]/div/div[1]/input').send_keys(Keys.DELETE)

    return process_transcript(transcript_list)

def process_transcript(transcript_list):
    transcript = []   
    # filter transcript: remove "•" markers and single letter icons before names
    j = 0
    while j < len(transcript_list):
        item = transcript_list[j]
            
        if item == "•":
            # Skip "•" markers
            j += 1
            continue
            
        # check if this is a single letter followed by a name (before "•")
        if (len(item) == 1 and item.isalpha() and 
            j + 2 < len(transcript_list) and 
            transcript_list[j + 2] == "•"):
            # skip single letter icon, keep the name that follows
            j += 1
            transcript.append(transcript_list[j])
        else:
            # keep everything else (phone numbers, timestamps, dialog text)
            transcript.append(item)
        
        j += 1
        
    # group data as [name, time, text]
    transcript = [transcript_list[k:k+3] for k in range(0, len(transcript_list), 3)]
    return "\n\n".join(f"{element[0]} • {element[1]}\n{element[2]}" for element in transcript) #string
