from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from app.services.browser_utils import create_driver, wait_and_find_element
from flask import current_app


def start_podium_subprocess():
    username = current_app.config['USERNAME']
    password = current_app.config['PASSWORD']
    url = current_app.config['PODIUM_URL']

    driver = create_driver()
    driver.get(url)

    # login
    #wait_and_find_element(driver, By.XPATH, '//*[@id="emailOrPhoneInput"]').send_keys(username)
    #wait_and_find_element(driver, By.XPATH, '//*[@id="emailOrPhoneInput"]').send_keys(Keys.RETURN)
    #time.sleep(2)
    #wait_and_find_element(By.XPATH, '//*[@id="passwordInput"]').send_keys(password)
    #wait_and_find_element(By.XPATH, '//*[@id="passwordInput"]').send_keys(Keys.RETURN)

    return driver

def perform_verification(driver, two_factor_code):
    wait_and_find_element(driver, By.XPATH, '//*[@id="emailOrPhoneInput"]').send_keys(two_factor_code) #TESTING

    #wait_and_find_element(driver, By.XPATH, '//*[@id="verificationCode"]').send_keys(two_factor_code)
    #wait_and_find_element(driver, By.XPATH, '//*[@id="verificationCode"]').send_keys(Keys.RETURN)
    #time.sleep(5)

def continue_podium_subprocess(driver):
    wait_and_find_element(driver, By.XPATH, '//*[@id="emailOrPhoneInput"]').send_keys(Keys.RETURN) #TESTING











