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
from email.message import EmailMessage

BASE_DIR = Path(__file__).resolve().parent


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
    driver.get(url='https://www.foodlion.com/weekly-specials/')
    # driver.get(url='https://www.linkedin.com')
    driver.implicitly_wait(10)
    driver.find_element(By.ID, "modal-close").click()
    time.sleep(1)
    driver.switch_to.frame(driver.find_element(By.CLASS_NAME, "wishabi-iframe"))
    zipcode_input = driver.find_element(By.XPATH, "//html/body//div[@class='postal_code_div']/input")
    zipcode_input.send_keys('85001')
    driver.find_element(By.CLASS_NAME, 'submit_postal_code').click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//html/body//button[@class='submit_store_select']").click()
    time.sleep(1)
    driver.switch_to.default_content()
    driver.find_element(By.XPATH, "//a[text()='customer service']").click()


    skip_for_now = driver.find_element(By.XPATH,
                                       '//footer[@class="kds-Modal-footer  SiteModal-Introducing Boost"]/div/button[2]')
    skip_for_now.click()
    click_on_element = driver.find_element(By.XPATH,
                                           "//button[@aria-label='Large Avocados, , $0.99 With Card . Select for details.']")
    click_on_element.click()
    driver.quit()




    # driver.find_element(By.XPATH, "//div[@class='kds-Modal-footer-buttons']/button[2]").click()
    all_buttons = driver.find_element(By.XPATH, "/html/body/flipp-router/flipp-publication-page/div/flipp-sfml-component/sfml-storefront/div/sfml-linear-layout/sfml-flyer-image[1]/div")
    # a_tag.click()
    e = driver.find_element(By.XPATH, "//a[@class='post-next pager-item']")
    location = e.location
    size = e.size
    w, h = size['width'], size['height']

    # driver.execute_script("window.scrollTo(90,212);")
    driver.execute_script(f"window.scrollTo({location['x']}, {location['y']});")

    # next = driver.find_element(By.LINK_TEXT, 'Next')
    next = driver.find_element(By.PARTIAL_LINK_TEXT, 'Next')
    next.click()
    # next = driver.find_element(By.XPATH, '//a[@class="post-next pager-item"]')
    # next.click()
    next_tab = driver.window_handles[-1]
    driver.switch_to.window(driver.window_handles[1])

    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # driver.find_element(By.XPATH, '//*[@id="chs-customer-insights-top"]/div/a').click()
    email = driver.find_element(By.ID, 'session_key')
    email.send_keys('023ajay.bhandari@gmail.com')
    password = driver.find_element(By.ID, 'session_password')
    password.send_keys('ajaylinkedin')
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'sign-in-form__submit-button'))).click()
    time.sleep(6)
    search = driver.find_element(By.XPATH, '//*[@id="global-nav-typeahead"]/input')
    search.send_keys('graphic designer')
    search.send_keys(Keys.ENTER)
    time.sleep(5)
    driver.find_element(By.XPATH, '//*[@id="search-reusables__filters-bar"]/div/div/button').click()
    time.sleep(5)
    jobs = driver.find_element(By.ID, 'ember422')
    jobs.click()
    # jobs.send_keys(Keys.DOWN)
    # jobs.send_keys(Keys.ENTER)
    time.sleep(5)
    print('hello')
except Exception as e_:
    print(e_)


