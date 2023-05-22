import logging
from mdintegrations import mdintegrations_api
from db_client import DBClient
from datetime import datetime


logger = logging.getLogger("create_new_mdcaseintegrations")

def create_new_mdcaseintegrations(email: str):
    try:
        db = DBClient()
        visit = db.get_visits_fields(email)
       
        patient_id = visit.get("patient_id")
        if patient_id is None:
            patient_id = 'NA'

        bmi = visit.get("bmi")
        if bmi is None:
            bmi = 'NA'

        weight = visit.get("weight")
        if weight is None:
            weight = 'NA'

        height = visit.get("height")
        if height is None:
            height = 'NA'
        
        result = weight/height**2
        bmi_result = float(703*result)
        
        time1 = input(datetime.date)
        time2 = input(datetime.date)
        past_medication = f"yes - {time1} - start date: {time2} - end date: Currently taking".format(time1, time2)

        if time1 is '' and time2 is '':
            past_medication = 'No'
        elif time1 is '' and time2 is not '':
                past_medication = 'No'
        elif time1 is not '' and time2 is '':
                    past_medication = 'No'

        data ={
            "patient_id": patient_id,
            "case_questions": [
                {
                    "question": "BMI",
                    "answer": bmi_result,
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Have you taken weight loss assisting medication in the past? ",
                    "answer": past_medication,
                    "type": "string",
                    "important": True
                },
                {
                    "question": "IMPORTANT: CHANGE PHARMACY TO PATIENT'S LOCAL PHARMACY CUREXA DOES NOT DO WEGOVY OR WEIGHT LOSS",
                    "answer": "IMPORTANT: CHANGE PHARMACY TO PATIENT'S LOCAL PHARMACY CUREXA DOES NOT DO WEGOVY OR WEIGHT LOSS",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "DO ANY OF THESE APPLY TO YOU? Eating Disorder Gallbladder Disease Drug Abuse Alcohol Abuse Recent Bariatric Surgery Pancreatitis None of these",
                    "answer": "No",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Have you ever tested positive for HIV, Herpes 1, Herpes 2, Syphilis, or Hepatitis C? If so which one(s) have you tested positive for?",
                    "answer": "No",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Are you currently pregnant?",
                    "answer": "No",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Have you ever participated in weight loss therapy?",
                    "answer": "Yes",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Have you ever attempted to lose weight in a weight management program, such as through caloric restriction, exercise, or behavior modification?",
                    "answer": "Yes",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Are you willing to reduce your caloric intake alongside medication?",
                    "answer": "Yes",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Are you willing to increase your physical activity alongside medication?",
                    "answer": "Yes",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Why do you want to lose weight with Wegovy?",
                    "answer": "Improve Physical Health and Lower A1C",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "Wegovy® Weight Loss Program",
                    "answer": "Yes",
                    "type": "string",
                    "important": True
                },
                {
                    "question": "TSH, Creatinine, A1c",
                    "answer": "Wegovy - Monthly Weight Loss Program: Monthly Wegovy Refills, Quarterly Metabolic Lab Testing & Analysis, Customized Weight-Loss Plan, Ongoing support and unlimited messaging with Expert Doctors",
                    "type": "string",
                    "important": True
                }
            ],
            "case_prescriptions": [
                {
                    "partner_medication_id": "8eb34cbb-8ae6-48db-83ff-2bc94e5c398f"
                }
            ],
        }
        # response = mdintegrations_api.create_case(data)
        logger.debug(data)
        return data 
    except Exception as e:
        logger.exception(e)
        return False





