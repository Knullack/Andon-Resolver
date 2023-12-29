import importlib
import subprocess
import sys
from time import sleep as s


try:
    importlib.import_module('selenium')
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.action_chains import ActionChains

except ModuleNotFoundError as e:
    print("Selenium Module Not found. Installing it now...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing Selenium: {e}")
        sys.exit(1)
try:
    importlib.import_module('keyboard')
    import keyboard
except ImportError:
    print("keyboard is not installed. Installing it now...")

    # Run a script to install Selenium using subprocess
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'keyboard'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing keyboard: {e}")
        sys.exit(1)

def HELPER_typeAndClick(element, textToType):
    element.send_keys(textToType)
    element.send_keys(Keys.ENTER)
def resolver():
    website_url = "http://fc-andons-na.corp.amazon.com/HDC3?category=Pick&type=No+Scannable+Barcode"
    optionals = ChromeOptions()
    optionals.add_argument('--log-level=3')
    optionals.add_argument('--force-device-scale-factor=0.7')
    optionals.add_argument('--disable-blink-features=AutomationControlled')
    optionals.add_argument('--disable-notifications')
    driver = webdriver.Chrome(options=optionals)
    driver.implicitly_wait(10)
    exceptionCount = 0
    while True:
        try:
            driver.get(website_url)
            break
        except WebDriverException as SE:
            print(f'WebDriverException #{exceptionCount}: Error in loading URL {SE.msg}\n')
            s(.3)
            exceptionCount += 1 if exceptionCount != 5 else sys.exit()
            # exceptionCount += 1
            # if exceptionCount == 5:
            #     print(f'{exceptionCount} WebDriverExceptions')
            #     sys.exit()

    elements = driver.find_elements('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/h1')
    if elements:
        url = "https://fcmenu-iad-regionalized.corp.amazon.com/login"
        driver.get(url)
        loginBadge = '13278440'
        input_element = driver.find_element('xpath', '//*[@id="badgeBarcodeId"]')
        HELPER_typeAndClick(input_element,loginBadge)

    driver.get(website_url)
    refreshLimit = 10
    refreshes = 0
    while refreshes <= refreshLimit:
        try:
            for x in range(1, 51):
                print(f'\nSession : {refreshes}')
                print(f"Andon #: {x}")
                selectAndon = driver.find_element('xpath', f'/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')
                driver.execute_script("arguments[0].scrollIntoView();", selectAndon)
                s(.8)            
                selectAndon.click()
                s(.8)
                viewAndon = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[2]/div[1]/div[1]/span/div/div[2]/awsui-button[2]/button')
                viewAndon.click()
                s(.8)
                resolve = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label/input')
                resolve.click()
                s(.8)
                saveChanges = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[3]/span/div/div[2]/awsui-button[2]/button')
                saveChanges.click()
        
        except AttributeError:
            print("\n\n ElementClickInterceptedException error\n\n")
            continue
        except Exception as e:
            print(f"An error occurred: \n\n{e}")
            continue
        finally:
            print(f"\n\nAndons resolved: {x}")
            if x == 50:
                driver.execute_script("location.reload();")
                print(f"\n\nRefreshing Page...") if refreshes != refreshLimit else None
                refreshes += 1   
            s(3)
    print(f"\n\nAndons in session resolved: {x}")
    driver.quit()

resolver()
