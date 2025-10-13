from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from app.services.browser_utils import create_driver, wait_and_find_element
from flask import current_app
import time


def start_glsa_subprocess():
    driver = create_driver()
    driver.maximize_window()
    driver.get(current_app.config['GLSA_URL'])
    
    # login link
    # wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/a').send_keys(Keys.RETURN) 
    # login button
    wait_and_find_element(driver, By.XPATH, '//*[@id="gb"]/div[2]/div[3]/div[1]/a').click()
    # username form
    wait_and_find_element(driver, By.XPATH, '//*[@id="identifierId"]').send_keys(current_app.config['USERNAME'])
    wait_and_find_element(driver, By.XPATH, '//*[@id="identifierNext"]/div/button').click()
    # password form
    wait_and_find_element(driver, By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input', timeout=120).send_keys(current_app.config['PASSWORD'])
    wait_and_find_element(driver, By.XPATH, '//*[@id="passwordNext"]/div/button').click()

    return driver


def continue_glsa_subprocess(driver, total_records):
    # select "Advantage Heating & Air Conditioning"
    wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/c-wiz/div/div[2]/div[2]/div[1]/span[1]/a').click()
    time.sleep(1)

    # select charge status dropdown
    wait_and_find_element(driver, By.CSS_SELECTOR, '[role="listbox"][aria-label="Charge phase filter"]').click()
    # select charged leads
    wait_and_find_element(driver, By.CSS_SELECTOR, 'div[role="option"][data-value="Charged leads"]').click()
    time.sleep(1)

    # select lead dropdown
    wait_and_find_element(driver, By.CSS_SELECTOR, '[role="listbox"][aria-label="Lead type filter"]').click()
    # select phone leads
    wait_and_find_element(driver, By.CSS_SELECTOR, 'div[role="option"][data-value="phone"]').click()
    time.sleep(1)

    # select time dropdown
    wait_and_find_element(driver, By.CSS_SELECTOR, 'span.A37UZe.sxyYjd.MQL3Ob').click()
    time.sleep(1)

    # set the dates



    # navigate to final page
    clicks_needed = calculate_clicks_to_last_page(total_records)

    for _ in range(clicks_needed):
        #next_button = WebDriverWait(driver, 5).until(
        #    EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[2]/span/div[2]/div/div[2]/c-wiz/div/span[2]/span[3]/span'))
        #)
        next_button = wait_and_find_element(By.CSS_SELECTOR, 'span[data-paginate="next"]')
        next_button.click()
        time.sleep(2)  # wait for page to load


def fill_form(driver, grade, grade_secondary, index):
    # select final lead
    wait_and_find_element(driver, By.CSS_SELECTOR, f'tr[data-row-id="{index}"]').click()
    #wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[3]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[11]/td[1]/div/span').text

    

    # wait for back button and click
    time.sleep(1)
    back_button = wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[1]/div/span/span/span')
    time.sleep(1)
    back_button.click()
    time.sleep(2)


def get_final_index(n: int) -> int:
    """calculate index of final record in table (set 20 records/page)"""
    remainder = n % 20
    #return 20 if remainder == 0 else remainder
    return 19 if remainder == 0 else remainder - 1


def calculate_clicks_to_last_page(n:int) -> int:
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
