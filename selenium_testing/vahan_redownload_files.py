import os
import re
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
BASE_DIR = Path(__file__).resolve().parent


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


def select_state(driver, wait, state_name):
    # driver.find_element(By.XPATH, '//*[@id="j_idt31_label"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt31_label"]'))).click()
    time.sleep(0.5)
    all_states = driver.find_elements(By.XPATH, '//*[@id="j_idt31_items"]/li')
    for state in all_states:
        if state.text.strip() == state_name:
            state.click()
            time.sleep(1)
            break


def select_rto(driver, wait, rto_name):
    # driver.find_element(By.XPATH, '//*[@id="selectedRto"]').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="selectedRto"]'))).click()
    all_rto = driver.find_elements(By.XPATH, f'//*[@id="selectedRto_panel"]/div/ul/li')
    for rto in all_rto:
        if rto.text.strip() == rto_name:
            rto.click()
            time.sleep(0.5)
            break


def click_toggle(drivers, wait):
    # drivers.find_element(By.XPATH, '//div[@id="filterLayout-toggler"]/span/a/span').click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@id="filterLayout-toggler"]/span/a/span'))).click()
    time.sleep(0.5)


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


def select_model(driver, wait, vehicle_type_name):
    # time.sleep(2)
    vehicle_xpath_map = {"THREE WHEELER (GOODS)": '//*[@id="VhClass"]/tbody/tr[58]/td/div/div[2]/span',
                         "THREE WHEELER (PASSENGER)": '//*[@id="VhClass"]/tbody/tr[59]/td/div/div[2]/span',
                         "THREE WHEELER (PERSONAL)": '//*[@id="VhClass"]/tbody/tr[60]/td/div/div[2]/span',
                         "E-RICKSHAW WITH CART (G)": '//*[@id="VhClass"]/tbody/tr[21]/td/div/div[2]/span',
                         "E-RICKSHAW(P)": '//*[@id="VhClass"]/tbody/tr[20]/td/div/div[2]/span'}
    if vehicle_type_name in vehicle_xpath_map:
        xpath = vehicle_xpath_map[vehicle_type_name]
        # driver.find_element(By.XPATH, xpath).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


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


def click_outer_refresh_button(drivers, wait):
    # time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.ID, 'j_idt61'))).click()
    # drivers.find_element(By.ID, 'j_idt61').click()
    time.sleep(0.5)


def click_inner_refresh(driver, wait):
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="j_idt66"]/span[2]'))).click()
    time.sleep(0.5)


def select_BS6(driver, wait):
    # selecting BS6
    # driver.find_element(By.XPATH, '//*[@id="norms"]/tbody/tr[10]/td/div/div[2]/span').click()
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="norms"]/tbody/tr[10]/td/div/div[2]/span'))).click()
    time.sleep(0.5)


def remove_previously_downloaded_csv(path):
    # use glob to get all files with the .xlsx extension
    xlsx_files = glob.glob(os.path.join(path, '*.xlsx'))
    if not xlsx_files:
        pass
    else:
        for file in xlsx_files:
            os.remove(file)


def read_error_file(todays_date, error_log_path):
    try:
        with open(error_log_path, 'r') as file:
            data_to_be_redownloaded = []
            content = file.readlines()

            # To test if error log file is properly reading use the following commented code

            # line = "2023-05-02 18:14:29,359 - vahan_logger - ERROR - Error for state-Madhya Pradesh(52),rto- ,model-THREE WHEELER (PASSENGER),fuel_type-ELECTRIC(BOV)\n"
            # line = "2023-05-02 17:36:48,273 - vahan_logger - ERROR - Error for state-Madhya Pradesh(52),rto-ANUPPUR DTO - MP65( 23-JUL-2022 ),model-THREE WHEELER (PASSENGER),fuel_type-PETROL\n"
            # line = "2023-05-02 18:03:19,401 - vahan_logger - ERROR - Error for state-Madhya Pradesh(52),rto-TIKAMGARH DTO - MP36( 23-JUL-2022 ),model-THREE WHEELER (PASSENGER),fuel_type-CNG ONLY\n"
            # if today_date in line.strip():
            #     state = re.search(r'state-(.*?),', line).group(1)
            #     rto = re.search(r'rto-(.*?)(?=,model-)', line).group(1).strip()
            #     if rto.strip():
            #         model = re.search(r'model-(.*?)(?=,fuel_type-)', line).group(1)
            #         fuel_type = re.search(r'fuel_type-(.*?)\n', line).group(1)
            #         data_to_be_redownloaded.append({"state": state,
            #                                         "rto": rto,
            #                                         "model": model,
            #                                         "fuel_type": fuel_type})
            #     else:
            #         pass
            #
            # return data_to_be_redownloaded

            for line in content:
                if todays_date in line.strip():
                    state = re.search(r'state-(.*?),', line).group(1)
                    rto = re.search(r'rto-(.*?)(?=,model-)', line).group(1)
                    if rto.strip():
                        model = re.search(r'model-(.*?)(?=,fuel_type-)', line).group(1)
                        fuel_type = re.search(r'fuel_type-(.*?)\n', line).group(1)
                        data_to_be_redownloaded.append({"state": state.strip(),
                                                        "rto": rto.strip(),
                                                        "model": model.strip(),
                                                        "fuel_type": fuel_type.strip()})
                    else:
                        pass

            return data_to_be_redownloaded

    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('ERROR IS ON LINE NO-----------', str(exc_tb.tb_lineno))
        print(e_)


def main(todays_date, error_log_path):
    try:
        logger = logger_config()
        driver, wait = common()
        files = read_error_file(todays_date, error_log_path)
        click_toggle(driver, wait)
        get_y_axis_items(driver, wait)
        # time.sleep(2)
        get_x_axis_items(driver, wait, value="Month Wise")
        # time.sleep(2)
        for file in files:
            select_state(driver, wait, file.get("state"))  # selecting state from the file
            select_rto(driver, wait, file.get("rto"))  # selecting rto from the file
            click_outer_refresh_button(driver, wait)
            select_model(driver, wait, file.get("model"))  # selecting model from the file
            select_fuel_type(driver, wait, file.get("fuel_type"))  # selecting fuel type from the file

            select_BS6(driver, wait)  # selecting BS6
            click_inner_refresh(driver, wait)

            # csv generating part
            table_check = driver.find_element(By.XPATH, '//tbody[@id="groupingTable_data"]//tr/td')
            if table_check.text == "No records found.":
                click_outer_refresh_button(driver, wait)
                print(f"No data available for-{file.get('state')},{file.get('rto')},{file.get('model')},{file.get('fuel_type')}")
                continue
            else:
                remove_previously_downloaded_csv(BASE_DIR)
                wait.until(EC.element_to_be_clickable((By.ID, 'groupingTable:j_idt75'))).click()  # downloading csv
                time.sleep(2)
                csv_store_path = os.path.join("data", str(datetime.now().date()))
                if not os.path.exists(os.path.join(BASE_DIR, csv_store_path)):
                    os.makedirs(os.path.join(BASE_DIR, csv_store_path))
                file_path = os.path.join(BASE_DIR, csv_store_path)
                file_name = f"{file.get('state').split('(')[0]}_{file.get('rto')}_{file.get('model')}_{file.get('fuel_type')}.xlsx"
                try:
                    shutil.copy2(os.path.join(BASE_DIR, 'reportTable.xlsx'), file_path)
                    os.rename(os.path.join(file_path, 'reportTable.xlsx'), os.path.join(file_path, file_name))
                    os.remove(os.path.join(BASE_DIR, 'reportTable.xlsx'))

                    # generating df and adding columns in csv
                    df = pd.read_excel(os.path.join(file_path, file_name), skiprows=3, index_col=1, engine="openpyxl")
                    fuel_type, model = model_type(file.get("fuel_type"), file.get("model"))
                    columns = df.columns
                    df = df.rename_axis('MAKER').reset_index()
                    df = df.drop(columns=['Unnamed: 0'])
                    df = df.rename(columns={columns[-1]: 'Total'})
                    df["MODEL"] = model
                    df["FUEL"] = fuel_type
                    df["TOWN"] = file.get("rto")
                    df["STATE"] = file.get('state').split("(")[0]

                    # save the DataFrame to a CSV file without the index
                    df.to_excel(os.path.join(file_path, file_name), index=False)

                    #  outer refresh button
                    click_outer_refresh_button(driver, wait)
                    print(f"Data available for-{file.get('state')},{file.get('rto')},{file.get('model')},{file.get('fuel_type')}")
                except Exception as err:
                    print(str(err))
                    logger.error(f"Error for state-{file.get('state')},rto-{file.get('rto')},model-{file.get('model')},fuel_type-{file.get('fuel_type')}")
                    continue
        driver.quit()
    except Exception as e_:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('ERROR IS ON LINE NO-----------', str(exc_tb.tb_lineno))
        print(e_)
        driver.quit()


if __name__ == "__main__":
    URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
    error_log_path = os.path.join(BASE_DIR, "logs", "error.log")
    todays_date = datetime.now().date().strftime('%Y-%m-%d')
    # todays_date = '2023-04-27'  # testing purpose
    main(todays_date, error_log_path)
