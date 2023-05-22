import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BASE_DIR = Path(__file__).resolve().parent
#
# chrome_path = f"{BASE_DIR}/chromedriver.exe"
# chrome_options = Options()
# chrome_service = Service(executable_path=chrome_path)
# driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
# driver.maximize_window()

def setUpModule():
    print("Starting module")

class AppTesting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Starting the application.")

    @classmethod
    def setUp(cls):
        print("This is the setup method.")

    def test_searchEngine(self):
        # driver.get(url='https://www.amazon.com/')
        print("This is google.com")

    def test_login(self):
        #  we can write scripts here.
        print("This is the login test.")

    def test_search(self):
        print("This is the search test.")

    @unittest.SkipTest
    def test_skippingTest(self):
        print("This will be skipped.")

    @unittest.skip("It is not ready yet.")
    def test_skippingTest_2(self):
        print("This will be skipped_2.")

    @unittest.skipIf(1 == 1, "This condition is not met.")
    def test_Condition_skipping(self):
        print("This will be Condition_skipping.")


    @classmethod
    def tearDown(cls):
        print("This is tear down method.")

    @classmethod
    def tearDownClass(cls):
        print("Closing the application.")

def tearDownModule():
    print("Ending module")

if __name__ == "__main__":
    unittest.main()
