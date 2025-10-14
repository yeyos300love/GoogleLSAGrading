from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from app.services.browser_utils import create_driver, wait_and_find_element
from app.services.browser_agent import run_agent
from flask import current_app
from datetime import datetime
from calendar import monthrange
import asyncio
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


def continue_glsa_subprocess(driver, total_records, start_date, end_date):
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

    now = datetime.now()
    prior_month = now.month - 1 if now.month > 1 else 12
    prior_year = now.year if now.month > 1 else now.year - 1
    last_day_prior = monthrange(prior_year, prior_month)[1]

    # check if date range is exactly last month
    if (start_date.day == 1 and 
        start_date.month == prior_month and 
        start_date.year == prior_year and
        end_date.day == last_day_prior and
        end_date.month == prior_month and
        end_date.year == prior_year):
        # click "Last Month"
        wait_and_find_element(driver, By.CSS_SELECTOR, 'div[data-value="last_month"]').click()
        time.sleep(1)
    # use custom date range
    else:
        start_date = start_date.strftime("%b %d %Y")
        end_date = end_date.strftime("%b %d %Y")

        wait_and_find_element(driver, By.CSS_SELECTOR, 'div[data-value="custom"]').click()
        # broswer-use agent help select correct dates
        asyncio.run(run_agent(start_date, end_date))
        # apply custom date
        wait_and_find_element(driver,By.CSS_SELECTOR, '[role="button"][aria-label="Apply"]').click()

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
    """
    GRADES = [
    "Very satisfied",                       index 1
    "Somewhat satisfied",
    "Neither satisfied nor dissatisfied",   index 3
    "Somewhat dissatisfied",
    "Very dissatisfied"]                    index 5
    """

    grade_secondary_index = convert_grade_secondary_to_index(grade_secondary)

    # select final lead
    wait_and_find_element(driver, By.CSS_SELECTOR, f'tr[data-row-id="{index}"]').click()
    #wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz/c-wiz/div[2]/div[3]/span/div[2]/div/div[1]/div/table/tbody[2]/tr[11]/td[1]/div/span').text

    rate_lead_button = wait_and_find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[2]/span/div[2]/div/div/div[1]/div[2]/div/button/span')
    time.sleep(1)
    rate_lead_button.click()

    # switch driver to iframe
    iframe = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'google-hats-survey_parent-dialog-dom'))
    )
    driver.switch_to.frame(iframe)

    if grade == 'Neither satisfied nor dissatisfied':
        # select grade
        wait_and_find_element(driver, By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[3]/div/button/div[2]').click()
        # switch driver to back original
        driver.switch_to.default_content()
        # "done" with form survey
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button').click()
        time.sleep(2)
        # archive lead
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[1]/span/span').click()
        time.sleep(1)

    elif grade == 'Very satisfied' and grade_secondary == 'Booked':
        # select grade
        wait_and_find_element(driver, By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[1]/div/button/div[2]').click()
        # select "Booked" as grade secondary
        wait_and_find_element(driver, By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[1]/sc-survey-single-select-button[1]/div').click()
        # switch driver to back original
        driver.switch_to.default_content()
        # "done" with form survery
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button').click()
        time.sleep(2)
        # mark as booked
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[2]/span/span').click()
        time.sleep(1)
        # save
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/div[5]/div/div[2]/div[3]/div[2]/span/span').click()
        time.sleep(1)

    elif grade == 'Very satisfied' and grade_secondary != 'Booked':
        # sleect grade
        wait_and_find_element(driver, By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[1]/div/button/div[2]').click()
        # select grade secondary
        wait_and_find_element(driver, By.XPATH, f'/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[1]/sc-survey-single-select-button[{grade_secondary_index}]/div').click()
        # switch driver to back original
        driver.switch_to.default_content()
        # "done" with form survey
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button').click()
        time.sleep(2)
        # archive lead
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[1]/span/span').click()
        time.sleep(1)

    elif grade == 'Very dissatisfied':
        # slect grade
        wait_and_find_element(driver, By.XPATH, '/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div/sc-survey-single-select-button[5]/div/button/div[2]').click()
        # select secondary grade
        wait_and_find_element(driver, By.XPATH, f'/html/body/sc-survey-survey-manager/div/div[2]/div/sc-survey-single-select-question/div[1]/sc-survey-single-select-button[{grade_secondary_index}]/div').click()
        # "done" with form survey
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/div[5]/div[2]/div/div[2]/div/button').click()
        time.sleep(2)
        # archive lead
        wait_and_find_element(driver, By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/c-wiz/div[1]/div[1]/div/div[2]/div[2]/div[1]/span/span').click()
        time.sleep(1)

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


def convert_grade_secondary_to_index(grade_secondary: str) -> int:
    """
    Convert a short grade_secondary value to its index.
    
    Args:
        grade_secondary (str): The short grade secondary value
        
    Returns:
        int: The index of the grade secondary, -1 if not found
    """

    GRADE_SECONDARY_POS = [
        "Booked",
        "Could convert to a booked client",
        "Relevant",
        "High value to the business",
        "Other"
    ]

    GRADE_SECONDARY_NEG = [
        "Outside service area",
        "Service not offered",
        "Not ready to book services",
        "Spam/Robocall",
        "Duplicate lead",
        "Employment/Sales Pitch",
        "Other"
    ]

    # Check if it's in the positive list
    if grade_secondary in GRADE_SECONDARY_POS:
        return GRADE_SECONDARY_POS.index(grade_secondary) + 1
    
    # Check if it's in the negative list
    elif grade_secondary in GRADE_SECONDARY_NEG:
        return GRADE_SECONDARY_NEG.index(grade_secondary) + 1
    
    # If not found in either list, return -1
    else:
        return -1
    