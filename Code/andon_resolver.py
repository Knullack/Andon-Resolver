import importlib
import subprocess
import tkinter as tk
from tkinter.constants import *
import sys
import logging
import subprocess
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By as by
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, ElementClickInterceptedException, WebDriverException, TimeoutException, InvalidSelectorException
from selenium.webdriver import Chrome

logging.basicConfig(level=logging.INFO)

class AndonResolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Andon Resolver")
        self.root.geometry("300x150")
        self.root.resizable(width=False, height=False)
        self.root.configure(background="white")
        self.badge = tk.IntVar()
        self.headless = tk.BooleanVar()
        self.output_text = tk.StringVar()
        self.output_text.set(value="")
        
        try:
            icon_path = 'Resources/Problem.ico'
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            None
        self.create_widgets(self.badge, self.headless, self.output_text)

    def create_widgets(self, badge, bool_head, output_text):
        # Labels
        labels = ["Badge Number:"]
        for i, text in enumerate(labels):
            label = tk.Label(self.root, text=text, font=("Arial", 10), fg="#333333", justify="center", background="white")
            label.place(x=10, y=50 + i * 70, width=100 if i == 0 else 160, height=25)

        # Entries
        entry_Badge = tk.Entry(self.root, borderwidth="2px", font=("Arial", 10), fg="#333333", justify="center", textvariable=badge)
        entry_Badge.delete(first=0)
        entry_Badge.place(x=110, y=50, height=30)
        entry_Badge.focus()

        # Checkbutton
        check_button = tk.Checkbutton(self.root, text="Hide Browser Window", font=("Arial", 10), fg="#333333", variable=bool_head, anchor='w', background="white")
        check_button.place(x=10, y=10, width=160, height=25, anchor=NW)

        # Button
        button = tk.Button(self.root, text="Resolve Andons", bg="#4CAF50", font=("Arial", 10, "bold"), fg="white", command=self.resolve)
        button.place(x=100, y=110, width=120, height=30)

        # Label
        output = tk.Label(self.root, textvariable=output_text, font=("Arial", 10), fg="#333333", justify="center", background="white", anchor='w')
        output.place(x=30, y=170, width=300, height=30)
        
    def resolve(self):
        try:
            badge_value = str(self.badge.get())
            boolean = self.headless.get()
            if badge_value:
                self.output_text.set("")  # Clear the output text if badge is not empty
                self.root.update()
                resolver(self.badge, boolean)
            else:
                self.output_text.set("Enter Valid Badge entry")
                self.root.update()
        except tk.TclError:
            self.output_text.set("Enter Valid Badge entry")
            self.root.update()

class resolver:
    def __init__(self, badge: int, headless: bool = False) -> None:
        self.badge = badge
        self.FCMenu_URL = 'https://fcmenu-iad-regionalized.corp.amazon.com/login'
        self.andon_site = "http://fc-andons-na.corp.amazon.com/HDC3?category=Pick&type=All+types"
        self.launch_chrome_with_remote_debugging(9200)
        optionals = ChromeOptions()
        optionals.add_argument('--log-level=3')
        optionals.add_argument('--force-device-scale-factor=0.7')
        optionals.add_argument('--disable-blink-features=AutomationControlled')
        optionals.add_argument('--disable-notifications')
        optionals.add_experimental_option("debuggerAddress", f"127.0.0.1:9200")
        if not headless:
            optionals.add_argument('--headless')
        self.driver = Chrome(options=optionals)
        self.main()

    def launch_chrome_with_remote_debugging(self, port) -> None:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        subprocess.Popen([chrome_path, f"--remote-debugging-port={port}"])

    def install_module(self, module_name: str) -> None:
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

    def navigate_to(self, url: str, max_attempts: int = 5) -> None:
        exception_count = 0
        while exception_count < max_attempts:
            try:
                self.driver.get(url)
                return
            except WebDriverException as se:
                exception_count += 1
                if "ERR_NAME_NOT_RESOLVED" in se.msg:
                    logging.error(f'WebDriverException #{exception_count}:\n Error in loading URL:: {se.msg}\n')
                else:
                    logging.error(f'WebDriverException #{exception_count}:\n Error in loading URL:: {se.msg}\n')
                
        sys.exit(1)

    def login(self) -> None:
        self.navigate_to(self.FCMenu_URL)
        input_element = self.driver.find_element('xpath', '//*[@id="badgeBarcodeId"]')
        self.type_and_click(input_element, self.badge)

    def type_and_click(self, element: object, str: str) -> None:
        element.send_keys(str)
        element.send_keys(Keys.ENTER)

    def start_resolving(self) -> None:
        self.navigate_to(self.andon_site)
        for x in range(1, 51):
            logging.info(f"Andon #: {x}")
            self.select_andon(x)
            self.resolve()
        
    def select_andon(self, x: int) -> None:
        actions = ActionChains(self.driver)
        while True:
            try:
                # wait for table to show
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[1]')))
                select_andon = self.driver.find_element('xpath', f'/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')
                break
            except NoSuchElementException:
                self.driver.execute_script('location.reload();')
                try:
                    select_andon = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[3]/table/tbody/tr[{x}]/td[1]/awsui-radio-button/div/label/input')))
                    break
                except InvalidSelectorException:
                    self.driver.execute_script('location.reload();')

        view_andon = self.driver.find_element('xpath', '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-table/div/div[2]/div[1]/div[1]/span/div/div[2]/awsui-button[2]/button')
        exceptionState = False
        # actions.move_to_element(select_andon).perform()
        
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
            self.driver.execute_script("location.reload();")
            self.start_resolving()

    def resolve(self) -> None:
        try:
            self.driver.implicitly_wait(.5)
            failed_warning_msg = self.driver.find_element(by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-flash/div/div[2]/div/div')
            failed_warning_msg = True
        except TimeoutException: 
            failed_warning_msg = False
        except NoSuchElementException:
            failed_warning_msg = False

        checkbox_state = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label'))).get_attribute('class')
        
        if checkbox_state == "awsui-checkbox": #unchecked
            try:
                resolve = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[2]/div/span/span/awsui-form/div/div[2]/span/span/awsui-form-section/div/div[2]/span/awsui-column-layout/div/span/div/awsui-form-field[4]/div/div/div/div/span/awsui-checkbox/label/input')))
                resolve.click()

                save_changes = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by.XPATH, '/html/body/div/div/div/awsui-app-layout/div/main/div/div[2]/div/span/div/awsui-modal/div[2]/div/div/div[3]/span/div/div[2]/awsui-button[2]/button')))
                save_changes.click()
            except NoSuchElementException:
                failed_warning_msg = True
            except ElementClickInterceptedException:
                failed_warning_msg = True
            except NoSuchWindowException:
                sys.exit()
            if failed_warning_msg:
                logging.info('Unable to update andon; exception occurred, refreshing page...')
                self.driver.execute_script("location.reload();")
                self.resolve_andons()
        elif checkbox_state == "awsui-checkbox awsui-checkbox-checked": # checked
            logging.info("Andon already resolved, refreshing page...")
            self.driver.execute_script("location.reload();")
        else: None

    def main(self):
        self.install_module('selenium')
        self.navigate_to(self.andon_site)
        # while self.driver.current_url != self.andon_site:
        #     self.navigate_to(self.andon_site)

        self.login()
        self.start_resolving()
        self.driver.quit()

if __name__ == "__main__":
    # root = tk.Tk()
    # app = AndonResolverApp(root)
    # root.mainloop()
    resolver(12730876, headless=False)