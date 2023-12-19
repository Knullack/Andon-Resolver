import importlib
import subprocess
import tkinter as tk
import tkinter.font as tkFont
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

        self.create_widgets()

    def create_widgets(self):
        # Labels
        labels = ["Badge Number", "Andons To Resolve (x50)"]
        for i, text in enumerate(labels):
            label = tk.Label(self.root, text=text, font=("Arial", 10), fg="#333333", justify="center", background="white")
            label.place(x=30, y=30 + i * 70, width=100 if i == 0 else 160, height=25)

        # Entries
        entries = ["Entry 1", "Entry 2"]
        for i, text in enumerate(entries):
            entry = tk.Entry(self.root, borderwidth="2px", font=("Arial", 10), fg="#333333", justify="center")
            entry.insert(0, text)
            entry.place(x=200, y=30 + i * 70, width=100, height=30)

        # Checkbutton
        check_button = tk.Checkbutton(self.root, text="Show Browser Window", font=(
            "Arial", 10), fg="#333333", variable=tk.BooleanVar(), anchor='w', background="white")
        check_button.place(x=400, y=30, width=160, height=25)

        # Button
        button = tk.Button(self.root, text="Resolve Andons", bg="#4CAF50", font=("Arial", 10, "bold"), fg="white", command=self.button_command)
        button.place(x=405, y=100, width=120, height=30)

        # ListBox
        # list_box = tk.Listbox(self.root, borderwidth="2px", font=(
        #     "Arial", 10), fg="#333333", selectbackground="#4CAF50", selectforeground="white")
        # list_box.place(x=30, y=150, width=540, height=300)

    def button_command(self):
        print("Button Command")


def window(main_func):
    def resolve_andons_with_input():
        badge_number = badge_entry.get()
        refresh_limit = refresh_entry.get()
        main_func(badge_number, refresh_limit)

    icon_name = 'Problem.ico'
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
            logging.error(
                f'WebDriverException #{exception_count}: Error in loading URL {se.msg}\n')
            s(0.3)
            exception_count += 1
    logging.error(f'{exception_count} WebDriverExceptions')
    sys.exit(1)


def login(driver, badge):
    input_element = driver.find_element('xpath', '//*[@id="badgeBarcodeId"]')
    HELPER_type_and_click(input_element, badge)


def HELPER_type_and_click(element, text_to_type):
    from selenium.webdriver.common.keys import Keys
    element.send_keys(text_to_type)
    element.send_keys(Keys.ENTER)


def resolve_andons(driver, refresh_limit):
    for x in range(1, int(refresh_limit) + 1):
        logging.info(f"Andon #: {x}")
        select_andon(driver, x)
        resolve_andon(driver)
        s(3)


def select_andon(driver, x):
    select_andon = driver.find_element(
        'xpath', f'/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')
    driver.execute_script("arguments[0].scrollIntoView();", select_andon)
    s(0.8)
    select_andon.click()
    s(0.8)
    view_andon = driver.find_element(
        'xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[2]/div[1]/div[1]/span/div/div[2]/awsui-button[2]/button')
    view_andon.click()
    s(0.8)


def resolve_andon(driver):
    resolve = driver.find_element(
        'xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label/input')
    resolve.click()
    s(0.8)
    save_changes = driver.find_element(
        'xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[3]/span/div/div[2]/awsui-button[2]/button')
    save_changes.click()


def main(badge_number, refresh_limit):
    install_module('selenium')
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    optionals = ChromeOptions()
    optionals.add_argument('--log-level=3')
    optionals.add_argument('--force-device-scale-factor=0.7')
    optionals.add_argument('--disable-blink-features=AutomationControlled')
    optionals.add_argument('--disable-notifications')

    driver = webdriver.Chrome(options=optionals)
    driver.implicitly_wait(10)

    navigate_to_website(driver, ANDON_SITE)
    login(driver, badge_number)
    # Redundant due to first driver navigation kicks out to FCMenu Login
    navigate_to_website(driver, ANDON_SITE)

    resolve_andons(driver, refresh_limit)

    logging.info(f"\n\nAndons in session resolved: {refresh_limit}")
    driver.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = AndonResolverApp(root)
    root.mainloop()
