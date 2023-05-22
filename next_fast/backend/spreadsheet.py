import requests
import json
import logging
import pygsheets
import pandas as pd

logger = logging.getLogger("fastapi")

class SpreadsheetAPI:
    def __init__(self):
        self.base_url = ''
 

    def write_spreadsheet_data(self, data):

        #authorization
        gc = pygsheets.authorize(service_file='teak-mantis-356816-c90d54a6344d.json')

        # Create empty dataframe
        df = pd.DataFrame()
        print(data['first_name'], '---------')

        # Create a column
        df['Date Requested'] = data['date_requested']
        df["Is the patient a policyholder?"] = data['is_patient_policy_holder']
        df["Patient First Name"] = data['first_name']
        df["Patient Last Name"] = data['last_name']
        df["Insurance Carrier"] = data['insurance_carrier']
        df["Insurance Member ID"] = data['insurance_member_id']
        df["Insurance Group Number"] = data['insurance_group_member']
        df["Patient Date of Birth"] = data['dob']
        df["Patient Email Address"] = data['email']
        df["Policy Holder First Name"] = data['policy_holder_first_name']
        df["Policy Holder Last Name"] = data['policy_holder_last_name']
        df["Policy Holder Date of Birth"] = data['policy_holder_dob']
        # df["Is the Patient Eligible?"] = data['is_patient_eligible']
        # df["Copay Amount"] = data['copay_amount']
        # df["Coinsurance Percentage"] = data['coinsurance_percentage']
        # df["Signed Off By"] = data['signed_off_by']
        # df["Date"] = data['date']
        # df["Has the Patient been notified?"] = data['has_patient_notified']

        #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        # sh = gc.open('Test_patient')
        
        # #select the first sheet 
        # wks = sh[0]

        # #update the first sheet with df, starting at cell B2. 
        # wks.set_dataframe(df,(2,1))

                #open the google spreadsheet 
        sh = gc.open('NextMedical -  Manual Eligibility Spreadsheet')

        #select the first sheet 
        wks = sh[0]

        #retrieve all rows of the worksheet
        cells = wks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')

        #extract all non empty rows
        nonEmptyRows = []
        for i in cells:
            if i != []:
                nonEmptyRows.append(i)

        #calculating the length 
        countOfnonEmptyRows = len(nonEmptyRows)
        type(countOfnonEmptyRows)

        #defining the data
        ls = [data['date_requested'], data['is_patient_policy_holder'], data['first_name'], data['last_name'], data['insurance_carrier'], data['insurance_member_id'], data['insurance_group_member'], data['dob'], data['email'], data['policy_holder_first_name'], data['policy_holder_last_name'], data['policy_holder_dob']]

        #inserting data 
        wks.insert_rows(countOfnonEmptyRows, values=ls, inherit=True) # here wks is the worksheet object
        

spreadsheet = SpreadsheetAPI()