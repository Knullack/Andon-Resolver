import importlib
import subprocess
import tkinter as tk
from tkinter.constants import *
import sys
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By as by
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, ElementClickInterceptedException, WebDriverException, TimeoutException, InvalidSelectorException
logging.basicConfig(level=logging.INFO)

DRIVER = None
ANDON_SITE = "http://fc-andons-na.corp.amazon.com/HDC3?category=Pick&type=All+types"
LOGIN_URL = "https://fcmenu-iad-regionalized.corp.amazon.com/login"

class AndonResolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Andon Resolver")
        self.root.geometry("600x200")
        self.root.resizable(width=False, height=False)
        self.root.configure(background="white")
        self.badge = tk.IntVar()
        self.count = tk.IntVar()
        self.headless = tk.BooleanVar()
        self.output_text = tk.StringVar()
        self.output_text.set(value="")
        
        try:
            icon_path = 'Resources/Problem.ico'
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            None
        self.create_widgets(self.badge, self.count, self.headless, self.output_text)

    def create_widgets(self, badge, count, bool_head, output_text):
        # Labels
        labels = ["Badge Number", "Andons To Resolve (x50)"]
        for i, text in enumerate(labels):
            label = tk.Label(self.root, text=text, font=("Arial", 10), fg="#333333", justify="center", background="white")
            label.place(x=30, y=30 + i * 70, width=100 if i == 0 else 160, height=25)

        # Entries
        entry_Badge = tk.Entry(self.root, borderwidth="2px", font=("Arial", 10), fg="#333333", justify="center", textvariable=badge)
        entry_Badge.delete(first=0)
        entry_Badge.place(x=200, y=30, width=100, height=30)
        entry_Badge.focus()

        entry_count = tk.Entry(self.root, borderwidth="2px", font=("Arial", 10), fg="#333333", justify="center", textvariable=count)
        entry_count.delete(first=0)
        entry_count.insert(0, "1")
        entry_count.place(x=200, y=30 + 70, width=100, height=30)

        # Checkbutton
        check_button = tk.Checkbutton(self.root, text="Hide Browser Window", font=("Arial", 10), fg="#333333", variable=bool_head, anchor='w', background="white")
        check_button.place(x=400, y=30, width=160, height=25)

        # Button
        button = tk.Button(self.root, text="Resolve Andons", bg="#4CAF50", font=("Arial", 10, "bold"), fg="white", command=self.resolve)
        button.place(x=405, y=100, width=120, height=30)

        # Label
        output = tk.Label(self.root, textvariable=output_text, font=("Arial", 10), fg="#333333", justify="center", background="white", anchor='w')
        output.place(x=30, y=170, width=300, height=30)
        
    def resolve(self):
        try:
            badge_value = str(self.badge.get())
            count_value = self.count.get()
            boolean = self.headless.get()
            if badge_value and count_value != "":
                count_value = int(count_value)
                self.output_text.set("")  # Clear the output text if badge is not empty
                self.root.update()
                main(badge_value, count_value, boolean)
            else:
                self.output_text.set("Enter Valid Badge/Count entry")
                self.root.update()
        except tk.TclError:
            self.output_text.set("Enter Valid Badge/Count entry")
            self.root.update()
        except NoSuchElementException as e:
            print(e)
        except ElementClickInterceptedException:
            DRIVER.execute_script("location.reload();")
        except Exception as e:
            print(e)


def install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        logging.info(f"{module_name} not found. Installing it now...")
        try:
            subprocess.run([sys.executable, '-m', 'pip',
                           'install', module_name], check=True)
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
            exception_count += 1
            if "ERR_NAME_NOT_RESOLVED" in se.msg:
                logging.error(f'WebDriverException #{exception_count}:\n Error in loading URL:: {se.msg}\n')
            else:
                logging.error(f'WebDriverException #{exception_count}:\n Error in loading URL:: {se.msg}\n')
            
    sys.exit(1)

def login(driver, badge):
    elements = driver.find_elements('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/h1')
    if elements:
        url = "https://fcmenu-iad-regionalized.corp.amazon.com/login"
        driver.get(url)
        loginBadge = badge
        input_element = driver.find_element('xpath', '//*[@id="badgeBarcodeId"]')
        HELPER_type_and_click(input_element,loginBadge)

def HELPER_type_and_click(element, text_to_type):
    element.send_keys(text_to_type)
    element.send_keys(Keys.ENTER)

def resolve_andons(driver, refresh_limit):
    refreshes = 0
    failedToUpdate = False
    while refreshes <= refresh_limit:
        # perform exception handling here!!!!!!!!!!!!!
        for x in range(1, 51):
            logging.info(f"Session: {refreshes}\nAndon #: {x}")
            select_andon(driver, x)
            resolve_andon(driver, refresh_limit, failedToUpdate)
            x = 0 if failedToUpdate == True else None
    
def select_andon(driver, x):
    actions = ActionChains(driver)
    selected = False
    while True:
        try:
            # wait for table to show
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[1]')))
            select_andon = driver.find_element('xpath', f'/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')
            break
        except NoSuchElementException:
            driver.execute_script('location.reload();')
            try:
                select_andon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')))
                break
            except InvalidSelectorException:
                driver.execute_script('location.reload();')
    view_andon = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[2]/div[1]/div[1]/span/div/div[2]/awsui-button[2]/button')
    exceptionState = False
    actions.move_to_element(select_andon).perform()
    
    try:
        select_andon.click()
        view_andon.click()
    except NoSuchElementException:
        exceptionState = True
    except ElementClickInterceptedException:
        exceptionState = True
    except NoSuchWindowException:
        sys.exit()
    if exceptionState:
        logging.info('Unable to update andon; exception occurred, refreshing page...')
        driver.execute_script("location.reload();")
        resolve_andons(driver, 1)
def resolve_andon(driver, refresh_limit, failBool):
    try:
        driver.implicitly_wait(.5)
        failed_warning_msg = driver.find_element(by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-flash/div/div[2]/div/div')
        failed_warning_msg = True
    except (TimeoutException, NoSuchElementException):
        failed_warning_msg = False
    checkbox_state = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label'))).get_attribute('class')
    
    if checkbox_state == "awsui-checkbox":
        try:
            resolve = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label/input')))
            resolve.click()

            save_changes = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[3]/span/div/div[2]/awsui-button[2]/button')))
            save_changes.click()
        except NoSuchElementException:
            failed_warning_msg = True
        except ElementClickInterceptedException:
            failed_warning_msg = True
        except NoSuchWindowException:
            sys.exit()
        if failed_warning_msg:
            logging.info('Unable to update andon; exception occurred, refreshing page...')
            driver.execute_script("location.reload();")
            resolve_andons(driver,refresh_limit)
    elif checkbox_state == "awsui-checkbox awsui-checkbox-checked":
        logging.info("Andon already resolved, refreshing page...")
        driver.execute_script("location.reload();")
        failBool = True
    else: None

def main(badge_number, refresh_limit, head):
    install_module('selenium')
    optionals = ChromeOptions()
    optionals.add_argument('--log-level=3')
    optionals.add_argument('--force-device-scale-factor=0.7')
    optionals.add_argument('--disable-blink-features=AutomationControlled')
    optionals.add_argument('--disable-notifications')

    if head:
        optionals.add_argument('--headless')
    

    DRIVER = webdriver.Chrome(options=optionals)
    DRIVER.implicitly_wait(10)

    navigate_to_website(DRIVER, ANDON_SITE, refresh_limit)
    login(DRIVER, badge_number)
    # Redundant due to first driver navigation kicks out to FCMenu Login
    navigate_to_website(DRIVER, ANDON_SITE, refresh_limit)

    resolve_andons(DRIVER, refresh_limit)

    logging.info(f"\n\nAndons in session resolved: {refresh_limit}")
    DRIVER.quit()

if __name__ == "__main__":
    # root = tk.Tk()
    # app = AndonResolverApp(root)
    # root.mainloop()
    main('12730876', 1, False)
