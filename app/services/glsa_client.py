from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from app.services.browser_utils import create_driver, wait_and_find_element
from flask import current_app


def form_completion():
    url = current_app.config['GLSA_URL']

    driver = create_driver()
    driver.get(url)
