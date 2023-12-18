import importlib
import subprocess
import sys
from time import sleep as s
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions

logging.basicConfig(level=logging.INFO)

ANDON_SITE = "http://fc-andons-na.corp.amazon.com/HDC3?category=Pick&type=No+Scannable+Barcode"
LOGIN_URL = "https://fcmenu-iad-regionalized.corp.amazon.com/login"
REFRESH_LIMIT = 10

def install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        logging.info(f"{module_name} not found. Installing it now...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', module_name], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error installing {module_name}: {e}")
            sys.exit(1)

def navigate_to_website(driver, url, max_attempts=5):
    exception_count = 0
    while exception_count < max_attempts:
        try:
            driver.get(url)
            return
        except WebDriverException as se:
            logging.error(f'WebDriverException #{exception_count}: Error in loading URL {se.msg}\n')
            s(0.3)
            exception_count += 1
    logging.error(f'{exception_count} WebDriverExceptions')
    sys.exit(1)

def login(driver, badge):
    input_element = driver.find_element('xpath', '//*[@id="badgeBarcodeId"]')
    HELPER_type_and_click(input_element, badge)

def HELPER_type_and_click(element, text_to_type):
    element.send_keys(text_to_type)
    element.send_keys(Keys.ENTER)

def resolve_andons(driver):
    for x in range(1, 51):
        logging.info(f'\nSession : {refreshes}')
        logging.info(f"Andon #: {x}")
        select_andon(driver, x)
        resolve_andon(driver)
        s(3)

def select_andon(driver, x):
    select_andon = driver.find_element('xpath', f'/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')
    driver.execute_script("arguments[0].scrollIntoView();", select_andon)
    s(0.8)
    select_andon.click()
    s(0.8)
    view_andon = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[2]/div[1]/div[1]/span/div/div[2]/awsui-button[2]/button')
    view_andon.click()
    s(0.8)

def resolve_andon(driver):
    resolve = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label/input')
    resolve.click()
    s(0.8)
    save_changes = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[3]/span/div/div[2]/awsui-button[2]/button')
    save_changes.click()

if __name__ == "__main__":
    install_module('selenium')

    optionals = ChromeOptions()
    optionals.add_argument('--log-level=3')
    optionals.add_argument('--force-device-scale-factor=0.7')
    optionals.add_argument('--disable-blink-features=AutomationControlled')
    optionals.add_argument('--disable-notifications')

    driver = webdriver.Chrome(options=optionals)
    driver.implicitly_wait(10)

    navigate_to_website(driver, ANDON_SITE)
    login(driver, '12730876')
    navigate_to_website(driver, ANDON_SITE)  # Redundant due to first driver navigation kicks out to FCMenu Login

    refreshes = 0
    x = 0
    while refreshes <= REFRESH_LIMIT:
        resolve_andons(driver)
        x += 1
        if refreshes == REFRESH_LIMIT:
            logging.info("\n\nRefreshing Page...")
            driver.execute_script("location.reload();")
        refreshes += 1

    logging.info(f"\n\nAndons in session resolved: {x}")
    driver.quit()
