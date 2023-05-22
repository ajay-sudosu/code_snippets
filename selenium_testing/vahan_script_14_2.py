import os
import sys
import time
import glob
import shutil
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
BASE_DIR = Path(__file__).resolve().parent


def initialize_directory():
    if not os.path.exists(os.path.join(BASE_DIR, "logs")):
        os.makedirs(os.path.join(BASE_DIR, "logs"))


def logger_config():
    # logging configurations
    # Create logger
    logger = logging.getLogger('vahan_logger')
    logger.setLevel(logging.DEBUG)

    # Create file handler and set level to DEBUG
    fh_debug = logging.FileHandler(os.path.join(BASE_DIR, "logs", 'debug.log'))
    fh_debug.setLevel(logging.DEBUG)

    # Create file handler and set level to ERROR
    fh_error = logging.FileHandler(os.path.join(BASE_DIR, "logs", 'error.log'))
    fh_error.setLevel(logging.ERROR)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to handlers
    fh_debug.setFormatter(formatter)
    fh_error.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(fh_debug)
    logger.addHandler(fh_error)
    return logger


def common():
    chrome_path = f"{BASE_DIR}/chromedriver"
    # fox_path = f"{BASE_DIR}/geckodriver.exe"
    chrome_options = Options()
    prefs = {'download.default_directory': str(BASE_DIR),  # set the download directory to the current working directory
             'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': True}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--headless')
    # fox_options = FirefoxOptions()
    chrome_service = Service(executable_path=chrome_path)
    web_driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    web_driver.maximize_window()
    wait = WebDriverWait(web_driver, 30)
    # driver = webdriver.Firefox(options=chrome_options, service=chrome_service)
    # driver = webdriver.Firefox()
    web_driver.implicitly_wait(10)
    web_driver.get(url=URL)
    time.sleep(3)
    return web_driver, wait


def get_states(drivers, wait, start=1):
    # drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt31_label"]'))).click()
    time.sleep(0.5)
    states = drivers.find_elements(By.XPATH, "//div[@id='j_idt31_panel']/div/ul/li")
    # drivers.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt31_label"]'))).click()
    # time.sleep(1)
    return len(states[start:])


def select_state(driver, i, wait):
    # driver.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt31_label"]'))).click()
    # time.sleep(1)
    # state = driver.find_element(By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[{i}]")
    state = wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[{i}]")))
    state_name = state.text
    state.click()
    time.sleep(0.5)
    # state = driver.find_element(By.XPATH, f"//div[@id='j_idt31_panel']/div/ul/li[8]")
    return state_name


def get_rto(drivers, wait, start=1):
    # drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]'))).click()
    time.sleep(0.5)
    rto_items = drivers.find_elements(By.XPATH, '//*[@id="selectedRto_panel"]/div/ul/li')
    # drivers.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="selectedRto"]'))).click()
    time.sleep(0.5)
    return len(rto_items[start:])


def select_rto(driver, wait, j):
    # driver.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]'))).click()
    time.sleep(0.5)
    # rto = driver.find_element(By.XPATH, f'//*[@id="selectedRto_panel"]/div/ul/li[{j}]')
    rto = wait.until(EC.visibility_of_element_located((By.XPATH, f'//*[@id="selectedRto_panel"]/div/ul/li[{j}]')))
    rto_name = rto.text
    rto.click()
    time.sleep(0.5)
    # rto = driver.find_element(By.XPATH, f'//*[@id="selectedRto_panel"]/div/ul/li[4]')
    return rto_name


def get_y_axis_items(drivers,wait, axis=None):
    if not axis:
        # drivers.find_element(By.XPATH, '//*[@id="yaxisVar"]').click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yaxisVar"]'))).click()
        time.sleep(1)
        y_axis_items = drivers.find_elements(By.XPATH, '//div[@id="yaxisVar_panel"]/div/ul/li')
        for item in y_axis_items:
            if item.text == "Maker":
                item.click()
                time.sleep(1)
                break


def get_x_axis_items(drivers, wait, axis=None, value="Month Wise"):
    if not axis:
        # drivers.find_element(By.XPATH, '//*[@id="xaxisVar"]').click()
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xaxisVar"]'))).click()
        time.sleep(1)
        x_axis_items = drivers.find_elements(By.XPATH, '//div[@id="xaxisVar_panel"]/div/ul/li')
        for item in x_axis_items:
            if item.text == value:
                item.click()
                time.sleep(1)
                break


def click_refresh_button(wait):
    # time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.ID, 'j_idt61'))).click()
    # drivers.find_element(By.ID, 'j_idt61').click()
    time.sleep(1)


def click_toggle(drivers, wait):
    # time.sleep(2)
    # drivers.find_element(By.XPATH, '//div[@id="filterLayout-toggler"]/span/a/span').click()
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="filterLayout-toggler"]/span/a/span'))).click()
    time.sleep(0.5)
    # time.sleep(2)


def select_vehicle_type(driver, wait, vehicle_type_name):
    vehicle_xpath_map = {"THREE WHEELER (GOODS)": '//*[@id="VhClass"]/tbody/tr[58]/td/div/div[2]/span',
                         "THREE WHEELER (PASSENGER)": '//*[@id="VhClass"]/tbody/tr[59]/td/div/div[2]/span',
                         "THREE WHEELER (PERSONAL)": '//*[@id="VhClass"]/tbody/tr[60]/td/div/div[2]/span',
                         "E-RICKSHAW WITH CART (G)": '//*[@id="VhClass"]/tbody/tr[21]/td/div/div[2]/span',
                         "E-RICKSHAW(P)": '//*[@id="VhClass"]/tbody/tr[20]/td/div/div[2]/span'}
    if vehicle_type_name in vehicle_xpath_map:
        xpath = vehicle_xpath_map[vehicle_type_name]
        # driver.find_element(By.XPATH, xpath).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        time.sleep(0.5)


def select_fuel_type(driver, wait, fuel_type):
    if "CNG ONLY" == fuel_type.strip():  # for CNG ONLY and Petrol / CNG
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[1]/td/div/div[2]/span').click()  # CNG ONLY
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[1]/td/div/div[2]/span'))).click()  # CNG ONLY
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[16]/td/div/div[2]/span').click()  # PETROL/CNG
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[16]/td/div/div[2]/span'))).click()  # PETROL/CNG
        time.sleep(0.5)

    elif "DIESEL" == fuel_type.strip():  # DIESEL
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[2]/td/div/div[2]/span').click()  # DIESEL
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[2]/td/div/div[2]/span'))).click()  # DIESEL
        time.sleep(0.5)

    elif "PETROL" == fuel_type.strip():  # PETROL/Petrol/LPG/LPG only
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[15]/td/div/div[2]/span').click()  # PETROL
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[15]/td/div/div[2]/span'))).click()  # PETROL
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[19]/td/div/div[2]/span').click()  # Petrol/LPG
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[19]/td/div/div[2]/span'))).click()  # Petrol/LPG
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[12]/td/div/div[2]/span').click()  # LPG only
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[12]/td/div/div[2]/span'))).click()  # LPG only
        time.sleep(0.5)

    elif "ELECTRIC(BOV)" == fuel_type.strip():  # ELECTRIC(BOV)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fuel"]/tbody/tr[8]/td/div/div[2]/span'))).click()  # ELECTRIC(BOV)
        # driver.find_element(By.XPATH, '//*[@id="fuel"]/tbody/tr[8]/td/div/div[2]/span').click()  # ELECTRIC(BOV)
        time.sleep(0.5)


def select_BS6(driver, wait):
    # selecting BS6
    # driver.find_element(By.XPATH, '//*[@id="norms"]/tbody/tr[10]/td/div/div[2]/span').click()
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="norms"]/tbody/tr[10]/td/div/div[2]/span'))).click()
    time.sleep(0.5)



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
    if "CNG" in fuel_type:
        fuel_type = "CNG/PET"
    elif "PETROL" in fuel_type:
        fuel_type = "LPG/PET"
    return fuel_type, model


def remove_previously_downloaded_csv(path):
    # use glob to get all files with the .xlsx extension
    xlsx_files = glob.glob(os.path.join(path, '*.xlsx'))

    if not xlsx_files:
        pass
    else:
        for file in xlsx_files:
            os.remove(file)


def main():
    try:
        logger = logger_config()
        driver, wait = common()
        click_toggle(driver, wait)
        get_y_axis_items(driver, wait)
        get_x_axis_items(driver, wait, value="Month Wise")
        all_states_len = get_states(driver, wait, start=1)
        start_state_from = 2
        start_rto_from = 2
        for i in range(start_state_from, all_states_len+1):
            state_name = select_state(driver, i, wait)
            all_rto_len = get_rto(driver, wait, start=1)
            data = {
                "CNG ONLY": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"],
                "DIESEL": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"],
                "ELECTRIC(BOV)": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)",
                                  "E-RICKSHAW WITH CART (G)", "E-RICKSHAW(P)"],
                "PETROL": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)"]
            }
            # data = {
            #     "CNG ONLY": ["THREE WHEELER (GOODS)"],
            # }

            for j in range(start_rto_from, all_rto_len+2):
                rto_name = select_rto(driver, wait, j)
                time.sleep(0.5)
                # outer refresh button
                click_refresh_button(wait)

                # selecting BS6
                select_BS6(driver, wait)

                for fuel_types in data:
                    select_fuel_type(driver, wait, fuel_types)
                    for model in data[fuel_types]:
                        select_vehicle_type(driver, wait, model)
                        # driver.find_element(By.XPATH, '//*[@id="j_idt66"]/span[2]').click()  # Inner refresh button
                        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt66"]/span[2]'))).click()  # Inner refresh button
                        time.sleep(1)

                        # csv generating part
                        remove_previously_downloaded_csv(BASE_DIR)
                        # table_check = driver.find_element(By.XPATH, '//tbody[@id="groupingTable_data"]//tr/td')
                        table_check = wait.until(EC.presence_of_element_located((By.XPATH, '//tbody[@id="groupingTable_data"]//tr/td')))
                        if table_check.text == "No records found.":
                            # click_refresh_button(wait)
                            # select_fuel_type(driver, wait, fuel_types)
                            select_vehicle_type(driver, wait, model)
                            print(f"No data available for- {state_name}, {rto_name}, {fuel_types}, {model}")
                            continue
                        else:
                            wait.until(EC.element_to_be_clickable((By.ID, 'groupingTable:j_idt75'))).click()  # downloading csv
                            # driver.find_element(By.ID, 'groupingTable:j_idt75').click()  # downloading csv
                            time.sleep(2)
                            csv_store_path = os.path.join("data", str(datetime.now().date()))
                            if not os.path.exists(os.path.join(BASE_DIR, csv_store_path)):
                                os.makedirs(os.path.join(BASE_DIR, csv_store_path))
                            file_path = os.path.join(BASE_DIR, csv_store_path)
                            file_name = f"{state_name.split('(')[0]}_{rto_name}_{model}_{fuel_types}.xlsx"
                            try:
                                shutil.copy2(os.path.join(BASE_DIR, 'reportTable.xlsx'), file_path)
                                os.rename(os.path.join(file_path, 'reportTable.xlsx'), os.path.join(file_path, file_name))
                                os.remove(os.path.join(BASE_DIR, 'reportTable.xlsx'))

                                # generating df and adding columns in csv
                                df = pd.read_excel(os.path.join(file_path, file_name), skiprows=3, index_col=1,
                                                   engine="openpyxl")
                                fuel_type, model = model_type(fuel_types, model)
                                columns = df.columns
                                df = df.rename_axis('MAKER').reset_index()
                                df = df.drop(columns=['Unnamed: 0'])
                                df = df.rename(columns={columns[-1]: 'Total'})
                                df["MODEL"] = model
                                df["FUEL"] = fuel_type
                                df["TOWN"] = rto_name
                                df["STATE"] = state_name.split("(")[0]

                                # save the DataFrame to a CSV file without the index
                                df.to_excel(os.path.join(file_path, file_name), index=False)

                                #  outer refresh button
                                click_refresh_button(wait)
                                select_BS6(driver, wait)
                                select_fuel_type(driver, wait, fuel_types)
                                print(f"Data available for- {state_name}, {rto_name}, {fuel_type}, {model}")
                            except Exception as err:
                                print(str(err))
                                # exc_type, exc_obj, exc_tb = sys.exc_info()
                                logger.error(f"Error for state-{state_name},rto-{rto_name},model-{model},fuel_type-"
                                             f"{fuel_types}")
                                continue
                    select_fuel_type(driver, wait, fuel_types)
        driver.quit()
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('ERROR IS ON LINE NO-----------', str(exc_tb.tb_lineno))
        print(str(e_))
        driver.quit()


if __name__ == "__main__":
    initialize_directory()
    main()
