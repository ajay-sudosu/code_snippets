from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import requests

BASE_DIR = Path(__file__).resolve().parent




def GetImageCookies():
    print('Extracting Browser Cookies')
    image_cookies = ''
    for cookie in driver.get_cookies():
        if cookie['name'] == 'ssc':
            image_cookies += 'ssc={};'.format(cookie['value'])
        elif cookie['name'] == 'ghsdfkjlksssalk35bbr':
            image_cookies += 'ghsdfkjlksssalk35bbr={};'.format(cookie['value'])
    # print(image_cookies)
    return image_cookies

def SaveImage(captcha_file = "master.jpg"):
    print('Saving the captcha image')
    header = {
    # 'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    # 'Accept-Language': 'en,en-US;q=0.9,ar;q=0.8',
    # 'Sec-Fetch-Site': 'same-origin',
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cookie': GetImageCookies(),
    'Host': 'masked',
    'Referer': 'masked',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"}

    pic = requests.get('https://freecarrierlookup.com/captcha/captcha.php', verify=False, headers=header)
    if pic.status_code == 200:
        with open(captcha_file, 'wb') as f:
            f.write(pic.content)

def SolveCapcha(captcha_file="master.jpg"):
    print('Solving the captcha image')
    ANTICAPTCHA_KEY = 'masked'
    result = ImageToTextTask.ImageToTextTask(
        anticaptcha_key=ANTICAPTCHA_KEY).captcha_handler(captcha_file=captcha_file)
    captcha_text = result['solution']['text']
    print('Captcha text is :', captcha_text)
    return captcha_text




# browser = webdriver.Firefox()
# url = 'https://masked/'
# browser.get(url)
# def Login():
#     SaveImage()
#     sleep(5)
#     username = browser.find_element_by_id("masked_username")
#     username.clear()
#     username.send_keys("testuser")
#     password = browser.find_element_by_id("masked")
#     password.clear()
#     password.send_keys("testpass")
#     captcha = browser.find_element_by_id("masked")
#     captcha.clear()
#     captcha_text = SolveCapcha()
#     captcha.send_keys(captcha_text)
#     login = browser.find_element_by_id("masked").click()
#     sleep(5)
#     err_message = browser.find_elements_by_id('masked')
#     if err_message :
#         if err_message[0].text == 'The verification code is incorrect.':
#             print(err_message[0].text)
#             return False
#     return True






chrome_path = f"{BASE_DIR}/chromedriver.exe"
# fox_path = f"{BASE_DIR}/geckodriver.exe"
chrome_options = Options()
# fox_options = FirefoxOptions()

chrome_service = Service(executable_path=chrome_path)

driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
# driver = webdriver.Firefox(options=chrome_options, service=chrome_service)
# driver = webdriver.Firefox()

driver.maximize_window()
wait = WebDriverWait(driver, 10)
try:
    driver.get(url='https://freecarrierlookup.com/')
    driver.implicitly_wait(10)
    country_code = driver.find_element(By.XPATH, '//*[@id="cc"]')
    country_code.send_keys(Keys.BACKSPACE*5)
    country_code.send_keys('91')
    phone_number = driver.find_element(By.XPATH, '//*[@id="phonenum"]')
    phone_number.send_keys('6397474002')
    SaveImage()
    driver.quit()
except Exception as e_:
    print(e_)


