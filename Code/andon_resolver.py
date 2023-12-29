import importlib
import subprocess
import tkinter as tk
from tkinter.constants import *
import sys
from os.path import join, dirname
from time import sleep as s
import logging

logging.basicConfig(level=logging.INFO)

ANDON_SITE = "http://fc-andons-na.corp.amazon.com/HDC3?category=Pick&type=No+Scannable+Barcode"
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
            icon_path = '../Resources/Problem.ico'
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
        from selenium.common.exceptions import NoSuchElementException
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
        except Exception as e:
            print(e)

def window(main_func):
    def resolve_andons_with_input():
        badge_number = badge_entry.get()
        refresh_limit = refresh_entry.get()
        main_func(badge_number, refresh_limit)

    icon_name = '../Resources/Problem.ico'
    icon_path = join(dirname(__file__), icon_name)
    window = tk.Tk()
    window.title("HDC3 Andon Resolver")
    window.configure(background='white')

    try:
        window.iconbitmap(icon_path)
    except tk.TclError:
        None
    window.resizable(False, False)

    # Calculate the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates for the Tk window
    x = (screen_width / 2) - (300 / 2)  # 300 is the width of the window
    y = (screen_height / 2) - (150 / 2)  # 150 is the height of the window

    # Set the dimensions of the window and its position
    window.geometry(f"300x150+{int(x)}+{int(y)}")

    # Frame 1 --------------------------------------------------------------------------
    badgeFrame = tk.Frame(master=window, background='gray')
    badge_label = tk.Label(master=badgeFrame, text="Badge Number:")
    badge_entry = tk.Entry(master=badgeFrame)

    badge_label.pack(side='left', padx=2, pady=5)
    badge_entry.pack(side='left', padx=2, pady=5)
    badge_entry.focus()
    badgeFrame.pack()
    # -----------------------------------------------------------------------------------

    # Frame 2 --------------------------------------------------------------------------
    R_frame = tk.Frame(master=window)
    refresh_label = tk.Label(master=R_frame, text="Andons to resolve (x50):")
    refresh_entry = tk.Entry(master=R_frame)

    refresh_label.pack(side='left', padx=3, pady=3)
    refresh_entry.pack(side='left')

    R_frame.pack()
    # -----------------------------------------------------------------------------------

    # Frame 3 --------------------------------------------------------------------------
    authorFrame = tk.Frame(master=window)
    author = tk.Label(master=authorFrame,
                      text="Author: nuneadon", font=("Amazon", 7))
    resolve_button = tk.Button(
        master=authorFrame, text="Resolve Andons", command=resolve_andons_with_input)

    author.pack(side=tk.BOTTOM, anchor=tk.SE)
    resolve_button.pack(side='right', padx=3, pady=3)
    authorFrame.pack()
    # -----------------------------------------------------------------------------------
    window.mainloop()

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
    from selenium.common.exceptions import WebDriverException
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
    from selenium.webdriver.common.keys import Keys
    element.send_keys(text_to_type)
    element.send_keys(Keys.ENTER)

def resolve_andons(driver, refresh_limit):
    refreshes = 0
    failedToUpdate = False
    while refreshes <= refresh_limit:
        for x in range(1, 51):
            logging.info(f"Session: {refreshes}\nAndon #: {x}")
            select_andon(driver, x)
            resolve_andon(driver, refresh_limit, failedToUpdate)
            x = 0 if failedToUpdate == True else None
    
def select_andon(driver, x):
    from selenium.webdriver.common.action_chains import ActionChains
    actions = ActionChains(driver)
    select_andon = driver.find_element('xpath', f'/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')
    view_andon = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[2]/div[1]/div[1]/span/div/div[2]/awsui-button[2]/button')
    
    actions.move_to_element(select_andon).perform()
    select_andon.click()
    view_andon.click()

def resolve_andon(driver, refresh_limit, failBool):
    driver.implicitly_wait(0.1)
    failed_warning_msg = driver.find_elements('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-flash/div/div[2]/div/div')
    resolve = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label/input')
    save_changes = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[3]/span/div/div[2]/awsui-button[2]/button')
    driver.implicitly_wait(10)

    checkbox_state = driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label').get_attribute('class')
    if checkbox_state == "awsui-checkbox":
        resolve.click()
        save_changes.click()
        if failed_warning_msg:
            logging.info('Unable to update andon, refreshing page...')
            driver.execute_script("location.reload();")
            resolve_andons(driver,refresh_limit)
    elif checkbox_state == "awsui-checkbox awsui-checkbox-checked":
        logging.info("Failed to update andon error. Refreshing page...")
        driver.execute_script("location.reload();")
        failBool = True
    else: None

def main(badge_number, refresh_limit, head):
    install_module('selenium')
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    optionals = ChromeOptions()
    optionals.add_argument('--log-level=3')
    optionals.add_argument('--force-device-scale-factor=0.7')
    optionals.add_argument('--disable-blink-features=AutomationControlled')
    optionals.add_argument('--disable-notifications')

    if head:
        optionals.add_argument('--headless')
    

    driver = webdriver.Chrome(options=optionals)
    driver.implicitly_wait(10)

    navigate_to_website(driver, ANDON_SITE, refresh_limit)
    login(driver, badge_number)
    # Redundant due to first driver navigation kicks out to FCMenu Login
    navigate_to_website(driver, ANDON_SITE, refresh_limit)

    resolve_andons(driver, refresh_limit)

    logging.info(f"\n\nAndons in session resolved: {refresh_limit}")
    driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AndonResolverApp(root)
    root.mainloop()