from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import time
import sys


BASE_DIR = Path(__file__).resolve().parent
URL = "https://www.instagram.com/accounts/login/"

def common():
    chrome_path = f"{BASE_DIR}/chromedriver"
    chrome_options = Options()
    chrome_service = Service(executable_path=chrome_path)
    web_driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    web_driver.maximize_window()
    wait = WebDriverWait(web_driver, 30)
    web_driver.implicitly_wait(10)
    web_driver.get(url=URL)

    # Wait for the page to load
    time.sleep(5)
    return web_driver, wait


def login(driver, USERNAME, PASSWORD):

    # Enter the username and password
    username_field = driver.find_element(By.NAME, "username")
    username_field.send_keys(USERNAME)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(PASSWORD)

    # Submit the login form
    password_field.send_keys(Keys.ENTER)

    # Wait for the page to load
    time.sleep(5)

# Navigate to the Instagram home page
# driver.get("https://www.instagram.com/")

# Wait for the page to load
# time.sleep(5)


def unread_messages(driver):

    # Extract the number of unread messages
    unread_messages_element = driver.find_element(By.XPATH, "//a[@href='/direct/inbox/']")
    unread_messages_count = int(unread_messages_element.text)


def like_comment(driver):
    # Extract the number of likes and comments on the latest post
    driver.get("https://www.instagram.com/p/<POST_ID>/")
    time.sleep(5)
    likes_count = int(driver.find_element(By.XPATH, "//a[@class='zV_Nj']/span").text)
    comments_count = len(driver.find_elements(By.XPATH, "//div[@class='C4VMK']/span"))


def instagram_main(username, password):
    try:
        driver, wait = common()
        login(driver, username, password)
        unread_messages(driver)
        like_comment(driver)
        driver.quit()

    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('ERROR IS ON LINE NO-----------', str(exc_tb.tb_lineno))
        print(e_)


if __name__ == '__main__':
    instagram_main("test_instagram_000", "testinstagram")


# Print the results
# print("Unread messages: ", unread_messages_count)
# print("Likes count: ", likes_count)
# print("Comments count: ", comments_count)
