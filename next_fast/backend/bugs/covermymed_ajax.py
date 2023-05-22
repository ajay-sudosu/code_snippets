from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.support.ui import WebDriverWait
import platform
import requests
import csv


chromedriver_path = './chromedriver.exe'
which_os = platform.system()
if which_os == 'Windows':
    chromedriver_path = '../../chromedriver.exe'


class CoverMedsAjax:

    def __init__(self):
        logging.debug("Initializing object...")
        chrome_options = Options()
        if which_os != 'Windows':
            chrome_options.add_argument("no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--headless")
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=2560,1440')
        # chrome_options.add_experimental_option('w3c', False)
        self.driver = webdriver.Chrome(options=chrome_options, executable_path=chromedriver_path)
        self.driver.implicitly_wait(20)
        self.wait = WebDriverWait(self.driver, 20)
        self.session = requests.Session()

    def login(self):
        logging.debug("Login...")
        self.driver.get("https://account.covermymeds.com/")
        username = self.wait.until(EC.element_to_be_clickable((By.NAME, "username")))
        username.send_keys("mdipas")
        password = self.wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        password.send_keys("2022JoinNext!")
        #  Login button
        button = self.wait.until(EC.element_to_be_clickable((By.NAME, "commit")))
        button.click()

    def ajax_scrapping(self):
        selenium_user_agent = self.driver.execute_script("return navigator.userAgent;")
        self.session.headers.update({"user-agent": selenium_user_agent})

        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

        response = self.session.get("https://www.covermymeds.com/ajax/list")

        print(response.json())


if __name__ == '__main__':
    ajax = CoverMedsAjax()
    ajax.login()
    ajax.ajax_scrapping()
