from pathlib import Path
import time
import os
import shutil
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
import pandas as pd
import glob

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
    WebDriverWait(web_driver, 30)
    # driver = webdriver.Firefox(options=chrome_options, service=chrome_service)
    # driver = webdriver.Firefox()
    web_driver.implicitly_wait(10)
    web_driver.get(url=URL)
    return web_driver


def get_states(drivers, start=1):
    drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    time.sleep(1)
    states = drivers.find_elements(By.XPATH, "//div[@id='j_idt31_panel']/div/ul/li")
    drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    time.sleep(1)
    return len(states[start:])


def select_state(driver, i):
    driver.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    # state = driver.find_element(By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[{i}]")
    state = driver.find_element(By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[5]")
    return state


def get_rto(drivers, start=1):
    drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    time.sleep(1)
    rto_items = drivers.find_elements(By.XPATH, '//*[@id="selectedRto_panel"]/div/ul/li')
    time.sleep(1)
    drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    return len(rto_items[start:])


def select_rto(driver, j):
    driver.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    rto = driver.find_element(By.XPATH, f'//*[@id="selectedRto_panel"]/div/ul/li[{j}]')
    return rto


def get_y_axis_items(drivers, axis=None):
    if not axis:
        drivers.find_element(By.XPATH, '//*[@id="yaxisVar"]').click()
        y_axis_items = drivers.find_elements(By.XPATH, '//div[@id="yaxisVar_panel"]/div/ul/li')
        for item in y_axis_items:
            if item.text == "Maker":
                time.sleep(2)
                item.click()
                break


def get_x_axis_items(drivers, axis=None, value="Month Wise"):
    if not axis:
        drivers.find_element(By.XPATH, '//*[@id="xaxisVar"]').click()
        x_axis_items = drivers.find_elements(By.XPATH, '//div[@id="xaxisVar_panel"]/div/ul/li')
        for item in x_axis_items:
            if item.text == value:
                time.sleep(2)
                item.click()
                break


def click_refresh_button(drivers):
    drivers.find_element(By.ID, 'j_idt61').click()
    time.sleep(1)


def click_toggle(drivers):
    time.sleep(2)
    drivers.find_element(By.XPATH, '//div[@id="filterLayout-toggler"]/span/a/span').click()
    time.sleep(2)


def select_vehicle_type(driver, vehicle_type_name):
    time.sleep(2)
    vehicle_xpath_map = {"THREE WHEELER (GOODS)": '//*[@id="VhClass"]/tbody/tr[58]/td/div/div[2]/span',
                         "THREE WHEELER (PASSENGER)": '//*[@id="VhClass"]/tbody/tr[59]/td/div/div[2]/span',
                         "THREE WHEELER (PERSONAL)": '//*[@id="VhClass"]/tbody/tr[60]/td/div/div[2]/span',
                         "E-RICKSHAW WITH CART (G)": '//*[@id="VhClass"]/tbody/tr[21]/td/div/div[2]/span',
                         "E-RICKSHAW(P)": '//*[@id="VhClass"]/tbody/tr[20]/td/div/div[2]/span'}
    if vehicle_type_name in vehicle_xpath_map:
        xpath = vehicle_xpath_map[vehicle_type_name]
        driver.find_element(By.XPATH, xpath).click()

    # if vehicle_type_name == "THREE WHEELER (GOODS)":
    #     driver.find_element(By.XPATH, '//*[@id="VhClass"]/tbody/tr[58]/td/div/div[2]/span').click()
    # elif vehicle_type_name == "THREE WHEELER (PASSENGER)":
    #     driver.find_element(By.XPATH, '//*[@id="VhClass"]/tbody/tr[59]/td/div/div[2]/span').click()
    # elif vehicle_type_name == "THREE WHEELER (PERSONAL)":
    #     driver.find_element(By.XPATH, '//*[@id="VhClass"]/tbody/tr[60]/td/div/div[2]/span').click()


def select_fuel_type(driver, fuel_type):
    fuel_list = driver.find_elements(By.XPATH, '//table[@id="fuel"]/tbody/tr/td//label')
    for fuel in fuel_list:
        if fuel.text == fuel_type:  # for CNG ONLY and Petrol / CNG
            driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[1]/td/div/div[2]/span').click()
            driver.find_element('//*[@id="fuel"]/tbody/tr[16]/td/div/div[2]/span').click()
            time.sleep(2)
            break
        elif fuel.text == fuel_type:  # DIESEL
            driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[2]/td/div/div[2]/span').click()
            time.sleep(2)
            break



        elif fuel == "":
            pass


        else:
            # ELECTRIC(BOV)
            driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[8]/td/div/div[2]/span').click()
            time.sleep(2)
            break


def model_type(fuel_type, model):
    if "ELECTRIC(BOV)" in fuel_type:
        if "E-RICKSHAW" and "(G)" in model:
            model = "CARGO"
            fuel_type = "L3"
        elif "E-RICKSHAW" and "(PASSENGER)" in model:
            model = "PAXX"
            fuel_type = "L3"
        else:
            if "(GOODS)" in model:
                model = "CARGO"
            else:
                model = "PAXX"
            fuel_type = "L5"
    else:
        if "(GOODS)" in model:
            model = "CARGO"
        else:
            model = "PAXX"
    return fuel_type, model


def remove_previously_downloaded_csv(path):
    # use glob to get all files with the .xlsx extension
    xlsx_files = glob.glob(os.path.join(path, '*.xlsx'))

    # xlsx_files = []
    # iterate over all files in the directory
    # for filename in os.listdir(path):
    #     # check if the file has a .xlsx extension
    #     if filename.endswith('.xlsx'):
    #         # add the file path to the list
    #         xlsx_files.append(os.path.join(path, filename))
    if not xlsx_files:
        pass
    else:
        for file in xlsx_files:
            os.remove(file)

try:
    driver = common()
    click_toggle(driver)
    all_states_len = get_states(driver, start=1)
    for i in range(2, all_states_len+1):
        state = select_state(driver, i)
        time.sleep(2)
        state_name = str(state.text)
        state.click()
        time.sleep(2)
        all_rto_len = get_rto(driver, start=1)
        time.sleep(2)
        get_y_axis_items(driver)
        time.sleep(2)
        get_x_axis_items(driver, value="Month Wise")
        time.sleep(2)
        data = {
            "CNG ONLY": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"],
            "DIESEL": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"],
            "ELECTRIC(BOV)": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)",
                              "E-RICKSHAW WITH CART (G)", "E-RICKSHAW(P)"],
            "Petrol": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"]
        }
        # data = {
        #     "CNG ONLY": ["THREE WHEELER (GOODS)"],
        # }
        for j in range(2, all_rto_len+2):
            rto = select_rto(driver, j)
            rto_name = str(rto.text)
            rto.click()
            time.sleep(2)
            # outer refresh button
            click_refresh_button(driver)
            time.sleep(1)

            sidebar_tables = driver.find_elements(By.XPATH, '//div[@id="j_idt67_content"]/div')
            for fuel_type in data:
                time.sleep(2)
                select_fuel_type(driver, fuel_type)
                for model in data[fuel_type]:
                    # selecting BS6
                    driver.find_element(By.XPATH, '//*[@id="norms"]/tbody/tr[10]/td/div/div[2]/span').click()
                    time.sleep(1)
                    select_vehicle_type(driver, model)
                    driver.find_element(By.XPATH, '//*[@id="j_idt66"]/span[2]').click()  # Inner refresh button

                    # csv generating part
                    remove_previously_downloaded_csv(BASE_DIR)
                    time.sleep(2)
                    table_check = driver.find_element(By.XPATH, '//tbody[@id="groupingTable_data"]//tr/td')
                    if table_check.text == "No records found.":
                        click_refresh_button(driver)
                        print(f"No data available for- {state_name}, {rto_name}, {fuel_type}, {model}")
                        continue
                    else:
                        driver.find_element(By.ID, 'groupingTable:j_idt75').click()  # downloading csv
                        time.sleep(6)
                        if not os.path.exists(os.path.join(BASE_DIR, "data")):
                            os.makedirs(os.path.join(BASE_DIR, "data"))
                        file_path = os.path.join(BASE_DIR, "data")
                        file_name = f"{state_name.split('(')[0]}_{rto_name.split('-')[0]}_{model}_{fuel_type}.xlsx"
                        shutil.copy2(os.path.join(BASE_DIR, 'reportTable.xlsx'), file_path)
                        os.rename(os.path.join(file_path, 'reportTable.xlsx'), os.path.join(file_path, file_name))
                        os.remove(os.path.join(BASE_DIR, 'reportTable.xlsx'))

                        # generating df and adding columns in csv
                        df = pd.read_excel(os.path.join(file_path, file_name), skiprows=3, index_col=1)
                        fuel_type, model = model_type(fuel_type, model)
                        columns = df.columns
                        df = df.rename_axis('MAKER').reset_index()
                        df = df.drop(columns=['Unnamed: 0'])
                        df = df.rename(columns={columns[-1]: 'Total'})
                        df["TOWN"] = rto_name
                        df["MODEL"] = model
                        df["FUEL"] = fuel_type
                        df["STATE"] = state_name.split("(")[0]

                        # save the DataFrame to a CSV file without the index
                        df.to_excel(os.path.join(file_path, file_name), index=False)

                        #  outer refresh button
                        click_refresh_button(driver)
                        print(f"Data available for- {state_name}, {rto_name}, {fuel_type}, {model}")
    driver.quit()


except Exception as e_:

    exc_type, exc_obj, exc_tb = sys.exc_info()
    print('ERROR IS ON LINE NO-----------', str(exc_tb.tb_lineno))
    print(e_)
    driver.quit()
