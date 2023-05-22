import sys
import time
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
BASE_DIR = Path(__file__).resolve().parent


def common():
    chrome_path = f"{BASE_DIR}/chromedriver"
    # fox_path = f"{BASE_DIR}/geckodriver.exe"
    chrome_options = Options()
    prefs = {'download.default_directory': str(BASE_DIR),  # set the download directory to the current working directory
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': True}
    chrome_options.add_experimental_option('prefs', prefs)
    # fox_options = FirefoxOptions()
    chrome_service = Service(executable_path=chrome_path)
    web_driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    web_driver.maximize_window()
    wait = WebDriverWait(web_driver, 30)
    # driver = webdriver.Firefox(options=chrome_options, service=chrome_service)
    # driver = webdriver.Firefox()
    web_driver.implicitly_wait(10)
    web_driver.get(url=URL)
    return web_driver, wait


def get_states(drivers, start=1):
    drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    time.sleep(1)
    states = drivers.find_elements(By.XPATH, "//div[@id='j_idt31_panel']/div/ul/li")
    drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    time.sleep(1)
    return len(states[start:])


def select_state(driver, i):
    driver.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    time.sleep(1)
    state = driver.find_element(By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[{i}]")
    # state = driver.find_element(By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[8]")
    return state


def get_rto(drivers, start=1):
    rto_names = []
    drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    time.sleep(1)
    rto_items = drivers.find_elements(By.XPATH, '//*[@id="selectedRto_panel"]/div/ul/li')
    for rto in rto_items:
        rto_names.append(rto.text)
    # time.sleep(1)
    drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    time.sleep(1)
    return len(rto_items[start:]), rto_names[1:]


def main():
    try:
        data = {
            "CNG ONLY": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"],
            "DIESEL": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"],
            "ELECTRIC(BOV)": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)",
                              "E-RICKSHAW WITH CART (G)", "E-RICKSHAW(P)"],
            "PETROL": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"]
        }
        state_rto_map = {}
        driver, wait = common()
        all_states_len = get_states(driver, start=1)
        start_state_from = 2
        for i in range(start_state_from, all_states_len+2):
            state = select_state(driver, i)
            time.sleep(1)
            state_name = str(state.text)
            state.click()
            time.sleep(1)

            # data = {
            #     "CNG ONLY": ["THREE WHEELER (GOODS)"],
            # }
            rto_len, rto_names = get_rto(driver)
            state_rto_map[state_name] = rto_names
            print(f"Done all combinations for state-{state_name}")

        for state_, rto_list in state_rto_map.items():
            for rto_ in rto_list:
                if "," in rto_:
                    rto_ = rto_.replace(",", " ")
                for fuel_types in data:
                    for model in data[fuel_types]:
                        with open("all_combinations.csv", "a") as file:
                            file.write(f"{state_},{rto_}, {fuel_types}, {model}\n")

        # creating a csv format
        df = pd.read_csv('all_combinations.csv', lineterminator='\n')
        df.to_csv("all_combinations.csv", header=['State', 'Rto', 'Fuel Type', 'Model'], index=False)
        driver.quit()
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('ERROR IS ON LINE NO-----------', str(exc_tb.tb_lineno))

        print(e_)
        driver.quit()


if __name__ == "__main__":
    main()

