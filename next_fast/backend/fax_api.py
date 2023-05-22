from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pdf2image import convert_from_bytes
import requests

import smtplib
import email.utils
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import csv, io
from email.mime.base import MIMEBase
import logging
import base64
import pymysql

from config import DB_ENDPOINT, DB_USERNAME, DB_PASSWORD, DB_NAME

logger = logging.getLogger("fastapi")

SENDER = 'nand@joinnextmed.com'
SENDERNAME = 'Next Medical'

USERNAME_SMTP = "AKIAQXYVC547EKFMCXHF"
PASSWORD_SMTP = "BIxfrtJ/H4/rA7JEdYLcnHlVmuHo8V/GYifovCNkwBg9"

HOST = "email-smtp.us-east-2.amazonaws.com"
PORT = 587


API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIyNDdiYjA1Ny0yZmY5LTRjYWMtOGVmNi01ODM5NzVlMTZiNWQiLCJhY2NvdW50SWQiOiIzYjg0YzU1OC05MjkwLTRiM2ItOWZiNC00MjBhNDM1ZjZhYmEiLCJpYXQiOjE2MjQ0MjIzMDh9.Pwz1dFfewtiIWDwzC32Ha3jUpS_Lf1oOrf19yzCNtDo"

headers = {'Authorization': f'Basic {API_KEY}'}

def generate_quest_pdf(test, is_insurance, name, dob_month, dob_date, dob_year, email, phone, sex, fax, mrn, insurance,region_no):
  
    logger.debug(is_insurance)
    logger.debug(test)
    template = ""
    if is_insurance == 1:
        questFirst = "./pdfs/new_req/Quest_cover_pb.pdf"
        if test == "STD Basic":
            if sex == "M":
                template = "./pdfs/new_req/std/quest_pb/STD_basic_male_quest_pb.pdf"
            else:
                template = "./pdfs/new_req/std/quest_pb/STD_basic_female_quest_pb.pdf"
        elif test == "STD Standard":
             if sex == "M":
                template = "./pdfs/new_req/std/quest_pb/STD_standard_male_quest_pb.pdf"
             else:
                template = "./pdfs/new_req/std/quest_pb/STD_standard_female_quest_pb.pdf"
        elif test == "Trichomoniasis":
             if sex == "M":
                template = "./pdfs/new_req/newFive/trich_male_quest_pb.pdf"
             else:
                template = "./pdfs/new_req/newFive/trich_female_quest_pb.pdf"
        elif test == "STD Complete":
             if sex == "M":
                template = "./pdfs/new_req/std/quest_pb/STD_complete_male_quest_pb.pdf"
             else:
                template = "./pdfs/new_req/std/quest_pb/STD_complete_female_quest_pb.pdf"
        elif test == "36 Food Allergy Panel":
            template = "./pdfs/new_req/pb/Food_allergy_quest_pb.pdf"
        elif test == "Celiac Complete":
            template = "./pdfs/new_req/pb/Celiac_quest_pb.pdf"
        elif test == "HIV Standard":
            template = "./pdfs/new_req/pb/HIV_standard_quest_pb.pdf"
        elif test == "Chlamydia":
            template = "./pdfs/newFive/chlamydia_quest_pb.pdf"      
        elif test == "Gonorrhea":
            template = "./pdfs/newFive/gonorrhea_quest_pb.pdf"      
        elif test == "HIV Complete":
            template = "./pdfs/new_req/pb/HIV_complete_quest_pb.pdf"
        elif test == "Herpes Standard":
            template = "./pdfs/new_req/pb/HSV_standard_quest_pb.pdf"
        elif test == "Herpes Complete":
            template = "./pdfs/new_req/pb/HSV_complete_quest_pb.pdf"
        elif test == "Thyroid Complete Panel":
            template = "./pdfs/new_req/pb/Thyroid_complete_quest_pb.pdf"
        elif test == "Thyroid Standard Panel":
            template = "./pdfs/new_req/pb/Thyroid_standard_quest_pb.pdf"
        elif test == "Mycoplasma & Ureaplasma":
            template = "./pdfs/newFive/myco_urea_quest_pb.pdf"
        elif test == "Complete Vitamin & Mineral Panel":
            template = "./pdfs/newFive/vitamin_complete_quest_pb.pdf"  
        elif test == "Thyroid Function Test":
            template = "./pdfs/new_req/pb/Thyroid_function_quest_pb.pdf"
        elif test == "Hemoglobin A1C Test":
            template = "./pdfs/quest/insurance/heartvitaminsleep/quest-heart-a1c-insurance.pdf"
        elif test == "Cholesterol & Lipids Panel":
            template = "./pdfs/quest/insurance/heartvitaminsleep/quest-heart-lipid-insurance.pdf"
        elif test == "Vitamin B Panel":
            template = "./pdfs/quest/insurance/heartvitaminsleep/quest-vitamin-vitb-insurance.pdf"
        elif test == "Vitamin D & Inflammation Test":
            template = "./pdfs/quest/insurance/heartvitaminsleep/quest-vitamin-vitd-insurance.pdf"
        elif test == "Sleep & Stress Hormone Test":
            template = "./pdfs/quest/insurance/heartvitaminsleep/quest-sleepstress-sleepstress-insurance.pdf"
        elif test == "Cortisol Test":
            template = "./pdfs/quest/insurance/heartvitaminsleep/quest-sleepstress-cortisol-insurance.pdf"
        elif test == "Female Hormone Complete":
            template = "./pdfs/new_req/pb/Female_hormone_quest_pb.pdf"
        elif test == "Female Hormone Standard":
            template = "./pdfs/new_req/pb/Ovarian_quest_pb.pdf"
        elif test == "Male Hormone Test":
            template = "./pdfs/new_req/pb/Male_hormone_quest_pb.pdf"
        elif test == "Male Hormone Standard":
            template = "./pdfs/quest/insurance/quest-testosterone-insurance.pdf"
        elif test == "Heavy Metals Test":
            template = "./pdfs/new_req/pb/Heavy_metals_quest_pb.pdf"
        elif test == "Lyme Disease Test":
            template = "./pdfs/quest/insurance/quest-lyme-insurance.pdf"
        elif test == "Herpes 1&2 Early Detection":
            template = "./pdfs/new_req/pb/HSV_early_quest_pb.pdf"
        elif test == "HIV P24 Antigen Early Detection":
            template = "./pdfs/new_req/pb/HIV_early_quest_pb.pdf"
        elif test == "Indoor and Outdoor Allergy":
            if(region_no == "1"):
                template = "./pdfs/quest/insurance/quest-allergies-io01-insurance.pdf"
            elif (region_no == "2"):
                template = "./pdfs/quest/insurance/quest-allergies-io02-insurance.pdf"
            elif (region_no == "3"):
                template = "./pdfs/new_req/pb/Allergy_region_3_quest_pb.pdf"
            elif (region_no == "4"):
                template = "./pdfs/quest/insurance/quest-allergies-io04-insurance.pdf"
            elif (region_no == "5"):
                template = "./pdfs/new_req/pb/Allergy_region_5_quest_pb.pdf"
            elif (region_no == "6"):
                template = "./pdfs/quest/insurance/quest-allergies-io06-insurance.pdf"
            elif (region_no == "7"):
                template = "./pdfs/quest/insurance/quest-allergies-io07-insurance.pdf"
            elif (region_no == "8"):
                template = "./pdfs/quest/insurance/quest-allergies-io08-insurance.pdf"
            elif (region_no == "9"):
                template = "./pdfs/new_req/pb/Allergy_region_9_quest_pb.pdf"
            elif (region_no == "10"):
                template = "./pdfs/quest/insurance/quest-allergies-io10-insurance.pdf"
            elif (region_no == "11"):
                template = "./pdfs/quest/insurance/quest-allergies-io11-insurance.pdf"
            elif (region_no == "12"):
                template = "./pdfs/quest/insurance/quest-allergies-io12-insurance.pdf"
            elif (region_no == "13"):
                template = "./pdfs/quest/insurance/quest-allergies-io13-insurance.pdf"
            elif (region_no == "14"):
                template = "./pdfs/quest/insurance/quest-allergies-io14-insurance.pdf"
            elif (region_no == "15"):
                template = "./pdfs/quest/insurance/quest-allergies-io15-insurance.pdf"
            elif (region_no == "16"):
                template = "./pdfs/quest/insurance/quest-allergies-io16-insurance.pdf"
            elif (region_no == "17"):
                template = "./pdfs/quest/insurance/quest-allergies-io17-insurance.pdf"
        else:
            template="./pdfs/quest_standard_m.pdf"              
    else:
        questFirst = "./pdfs/new_req/Quest_Portal_Requisition_Client_Bill.pdf"
        if test == "STD Basic":
            if sex == "M":
                template = "./pdfs/new_req/std/quest_cb/STD_basic_male_quest_cb.pdf"
            else:
                template = "./pdfs/new_req/std/quest_cb/STD_basic_female_quest_cb.pdf"
        elif test == "STD Standard":
             if sex == "M":
                template = "./pdfs/new_req/std/quest_cb/STD_standard_male_quest_cb.pdf"
             else:
                template = "./pdfs/new_req/std/quest_cb/STD_standard_female_quest_cb.pdf"
        elif test == "STD Complete":
             if sex == "M":
                template = "./pdfs/new_req/std/quest_cb/STD_complete_male_quest_cb.pdf"
             else:
                template = "./pdfs/new_req/std/quest_cb/STD_complete_female_quest_cb.pdf"
        elif test == "36 Food Allergy Panel":
               template = "./pdfs/new_req/cb/Food_allergy_quest_cb.pdf"
        elif test == "Celiac Complete":
               template = "./pdfs/new_req/cb/Celiac_quest_cb.pdf"
        elif test == "HIV Standard":
            template = "./pdfs/new_req/cb/HIV_standard_quest_cb.pdf"      
        elif test == "Gonorrhea":
            template = "./pdfs/newFive/gonorrhea_quest_cb.pdf"   
        elif test == "Trichomoniasis":
             if sex == "M":
                template = "./pdfs/new_req/newFive/trich_male_quest_cb.pdf"
             else:
                template = "./pdfs/new_req/newFive/trich_female_quest_cb.pdf"
        elif test == "Chlamydia":
               template = "./pdfs/newFive/chlamydia_quest_cb.pdf"     
        elif test == "Complete Vitamin & Mineral Panel":
            template = "./pdfs/newFive/vitamin_complete_quest_cb.pdf"   
        elif test == "Mycoplasma & Ureaplasma":
            template = "./pdfs/newFive/myco_urea_quest_cb.pdf"
        elif test == "HIV Complete":
            template = "./pdfs/new_req/cb/HIV_complete_quest_cb.pdf"
        elif test == "Herpes Standard":
            template = "./pdfs/new_req/cb/HSV_standard_quest_cb.pdf"       
        elif test == "Herpes Complete":
            template = "./pdfs/new_req/cb/HSV_complete_quest_cb.pdf"       
        elif test == "Thyroid Complete Test":
            template = "./pdfs/new_req/cb/Thyroid_complete_quest_cb.pdf"
        elif test == "Thyroid Standard Test":
            template = "./pdfs/new_req/cb/Thyroid_standard_quest_cb.pdf"
        elif test == "Thyroid Function Test":
            template = "./pdfs/new_req/cb/Thyroid_function_quest_cb.pdf"
        elif test == "Metabolism Test":
            template = "./pdfs/quest/patient/quest-metabolism-patient.pdf"
        elif test == "Hemoglobin A1C Test":
            template = "./pdfs/quest/patient/heartvitaminsleep/quest-heart-a1c-patient.pdf"
        elif test == "Cholesterol & Lipids Panel":
            template = "./pdfs/quest/patient/heartvitaminsleep/quest-heart-lipid-patient.pdf"
        elif test == "Vitamin B Panel":
            template = "./pdfs/quest/patient/heartvitaminsleep/quest-vitamin-vitb-patient.pdf"
        elif test == "Vitamin D & Inflammation Test":
            template = "./pdfs/quest/patient/heartvitaminsleep/quest-vitamin-vitd-patient.pdf"
        elif test == "Sleep & Stress Hormone Test":
            template = "./pdfs/quest/patient/heartvitaminsleep/quest-sleepstress-sleepstress-patient.pdf"
        elif test == "Cortisol Test":
            template = "./pdfs/quest/patient/heartvitaminsleep/quest-sleepstress-cortisol-patient.pdf"
        elif test == "Female Hormone Complete":
            template = "./pdfs/new_req/cb/Female_hormone_quest_cb.pdf"
        elif test == "Female Hormone Standard":
            template = "./pdfs/new_req/cb/Ovarian_quest_cb.pdf"
        elif test == "Male Hormone Test":
            template = "./pdfs/new_req/cb/Male_hormone_quest_cb.pdf"
        elif test == "Male Hormone Standard":
            template = "./pdfs/quest/patient/quest-testosterone-patient.pdf"
        elif test == "Heavy Metals Test":
            template = "./pdfs/new_req/cb/Heavy_metals_quest_cb.pdf"
        elif test == "Lyme Disease Test":
            template = "./pdfs/quest/patient/quest-lyme-patient.pdf"
        elif test == "Indoor and Outdoor Allergy":
            if(region_no == "1"):
                template = "./pdfs/quest/patient/quest-allergies-io01-patient.pdf"
            elif (region_no == "2"):
                template = "./pdfs/quest/patient/quest-allergies-io02-patient.pdf"
            elif (region_no == "3"):
                template = "./pdfs/new_req/cb/Allergy_region_3_quest_cb.pdf"
            elif (region_no == "4"):
                template = "./pdfs/quest/patient/quest-allergies-io04-patient.pdf"
            elif (region_no == "5"):
                template = "./pdfs/new_req/cb/Allergy_region_5_quest_cb.pdf"
            elif (region_no == "6"):
                template = "./pdfs/quest/patient/quest-allergies-io06-patient.pdf"
            elif (region_no == "7"):
                template = "./pdfs/quest/patient/quest-allergies-io07-patient.pdf"
            elif (region_no == "8"):
                template = "./pdfs/quest/patient/quest-allergies-io08-patient.pdf"
            elif (region_no == "9"):
                template = "./pdfs/new_req/cb/Allergy_region_9_quest_cb.pdf"
            elif (region_no == "10"):
                template = "./pdfs/quest/patient/quest-allergies-io10-patient.pdf"
            elif (region_no == "11"):
                template = "./pdfs/quest/patient/quest-allergies-io11-patient.pdf"
            elif (region_no == "12"):
                template = "./pdfs/quest/patient/quest-allergies-io12-patient.pdf"
            elif (region_no == "13"):
                template = "./pdfs/quest/patient/quest-allergies-io13-patient.pdf"
            elif (region_no == "14"):
                template = "./pdfs/quest/patient/quest-allergies-io14-patient.pdf"
            elif (region_no == "15"):
                template = "./pdfs/quest/patient/quest-allergies-io15-patient.pdf"
            elif (region_no == "16"):
                template = "./pdfs/quest/patient/quest-allergies-io16-patient.pdf"
            elif (region_no == "17"):
                template = "./pdfs/quest/patient/quest-allergies-io17-patient.pdf"

    if template != "":
        if test == "STD Basic" or test == "STD Standard" or test == "STD Complete" or test == "Herpes Complete" or test == "Herpes Standard" or test == "HIV Standard" or test == "HIV Complete" or test == "Heavy Metals Test" or test == "Female Hormone Standard" or test == "Thyroid Complete Panel" or test == "HIV P24 Antigen Early Detection" or test == "Herpes 1&2 Early Detection" or test == "Thyroid Function Test" or test == "Thyroid Standard Panel" or test == "Female Hormone Complete" or test == "Male Hormone Test" or test == "36 Food Allergy Panel" or test == "Celiac Complete" or (test == "Indoor and Outdoor Allergy" and region_no == "3") or (test == "Indoor and Outdoor Allergy" and region_no == "5") or (test == "Indoor and Outdoor Allergy" and region_no == "9") : 
            logger.debug(template)
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFillColorRGB(0, 0, 0)
            can.setFont("Courier", 10)
            can.drawString(160, 378, f"{name}")
            can.drawString(160, 354, f"{dob_month}/{dob_date}/{dob_year}")
            can.drawString(160, 366, sex)
            if len(insurance.split(",")) == 3:
                insurance_arr = insurance.split(",")
                insurance_id = insurance_arr[0]
                insurance_name = insurance_arr[1]
                insurance_group = insurance_arr[2]

                can.drawString(405, 355, insurance_id)
                can.drawString(405, 378, insurance_name)
                can.drawString(406, 331, insurance_group)
            can.save()
    
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
    
            existing_pdf = PdfFileReader(open(template, "rb"))
            first_page = PdfFileReader(open(questFirst,"rb"))
            output = PdfFileWriter()
    
            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(first_page.getPage(0))
            output.addPage(page)
    
            outputStream = io.BytesIO()
            # outputStream = open("destination.pdf", "wb")
            output.write(outputStream)
            
            outputStream.seek(0)
            pdf_bytes = outputStream.read()
            outputStream.seek(0)
            pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
    
            connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
            connection.commit()
            cursor = connection.cursor()
            cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
            if (len(list(cursor.fetchall())) > 0):
                logger.debug("existing visit")
                cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
            else:
                cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
            connection.commit()
            connection.close()
    
            # final = convert_from_bytes(pdf_bytes)
            # outputStream.close()
    
            # final_bytes = io.BytesIO()
            # final[0].save(final_bytes, format="JPEG")
    
            # final_bytes.seek(0)
            # files = {
            #     'attachments': ('test.jpg', final_bytes,'image/jpeg')
            # }
            # form_data = {
            #     'faxNumber': fax,
            #     'coverPage': 'false'
            # }
    
            # url = 'https://api.documo.com/v1/faxes'
            # r = requests.post(url, headers=headers, files=files, data=form_data, verify=False)
    
            # return r.json()
            return "Success"
        else:
            logger.debug(template)
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFillColorRGB(0, 0, 0)
            can.setFont("Courier", 10)
    
            # can.drawString(70, 435, "212-530-7891")
    
            first_name = name.split(" ")[0]
    
            try:
                last_name = name.split(" ")[1]
            except:
                last_name = ""
            can.drawString(360, 767, f"{last_name}, {first_name}")
    
            can.drawString(495, 732, str(dob_month))
            can.drawString(523, 732, str(dob_date))
            can.drawString(548, 732, str(dob_year))
            can.drawString(598, 732, sex)
    
            can.drawString(370, 705, email)
    
            can.drawString(500, 675, phone)
    
            if len(insurance.split(",")) == 3:
                insurance_arr = insurance.split(",")
                insurance_id = insurance_arr[0]
                insurance_name = insurance_arr[1]
                insurance_group = insurance_arr[2]
    
                can.drawString(330, 546, insurance_id)
                can.drawString(330, 569, insurance_name)
                can.drawString(490, 546, insurance_group)
    
            # if is_insurance != 1:
            #     can.drawString(280, 757, "✔")
            can.save()
    
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
    
            existing_pdf = PdfFileReader(open(template, "rb"))
            first_page = PdfFileReader(open(questFirst,"rb"))
            output = PdfFileWriter()
    
            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(first_page.getPage(0))
            output.addPage(page)
    
            outputStream = io.BytesIO()
            # outputStream = open("destination.pdf", "wb")
            output.write(outputStream)
            
            outputStream.seek(0)
            pdf_bytes = outputStream.read()
            outputStream.seek(0)
            pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
    
            connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
            connection.commit()
            cursor = connection.cursor()
            cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
            if (len(list(cursor.fetchall())) > 0):
                logger.debug("existing visit")
                cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
            else:
                cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
            connection.commit()
            connection.close()
    
            # final = convert_from_bytes(pdf_bytes)
            # outputStream.close()
    
            # final_bytes = io.BytesIO()
            # final[0].save(final_bytes, format="JPEG")
    
            # final_bytes.seek(0)
            # files = {
            #     'attachments': ('test.jpg', final_bytes,'image/jpeg')
            # }
            # form_data = {
            #     'faxNumber': fax,
            #     'coverPage': 'false'
            # }
    
            # url = 'https://api.documo.com/v1/faxes'
            # r = requests.post(url, headers=headers, files=files, data=form_data, verify=False)
    
            # return r.json()
            return "Success"
    else:
        return "Failed"
    
def generate_labcorp_pdf(test, is_insurance, name, dob_month, dob_date, dob_year, email, phone, sex, fax, mrn, insurance,region_no):
    labcorpFirst = './pdfs/new_req/Labcorp_Portal_Requisition_Insurance_Bill.pdf'
    template = ""
    data = ""
    logger.debug(region_no)
    logger.debug(is_insurance)
    logger.debug(test)
    if is_insurance == 1:
        if test == "STD Basic":
            template = "./pdfs/new_req/std/labcorp_pb/STD_basic_labcorp_pb.pdf"
        elif test == "STD Standard":
            template = "./pdfs/new_req/std/labcorp_pb/STD_standard_labcorp_pb.pdf"
        elif test == "STD Complete":
            template = "./pdfs/new_req/std/labcorp_pb/STD_complete_labcorp_pb.pdf"
        elif test == "36 Food Allergy Panel":
            template = "./pdfs/new_req/Archive/Food_allergy_labcorp_pb.pdf"
        elif test == "Celiac Complete":
            template = "./pdfs/new_req/Archive/Celiac_labcorp_pb.pdf"
        elif test == "HIV Complete":
            template = "./pdfs/new_req/Archive/HIV_complete_labcorp_pb.pdf"
        elif test == "HIV Standard":
            template = "./pdfs/new_req/Archive/HIV_standard_labcorp_pb.pdf"
        elif test == "Herpes Standard":
            template = "./pdfs/new_req/Archive/HSV_standard_labcorp_pb.pdf"
        elif test == "Herpes Complete":
            template = "./pdfs/new_req/Archive/HSV_complete_labcorp_pb.pdf"
        elif test == "Thyroid Function Test":
            template = "./pdfs/new_req/Archive/Thyroid_function_labcorp_pb.pdf"
        elif test == "Thyroid Standard Panel":
            template =  "./pdfs/new_req/Archive/Thyroid_standard_labcorp_pb.pdf"
        elif test == "Thyroid Complete Panel":
            template =  "./pdfs/new_req/Archive/Thyroid_complete_labcorp_pb.pdf"
        elif test == "Hemoglobin A1C Test":
            template = "./pdfs/new_req/Archive/A1c_labcorp_pb.pdf"
        elif test == "Cholesterol & Lipids Panel":
            template =  "./pdfs/new_req/Archive/Lipids_labcorp_pb.pdf"
        elif test == "Vitamin B Panel":
            template = "./pdfs/new_req/Archive/Vitamin_b_labcorp_pb.pdf"
        elif test == "Vitamin D & Inflammation Test":
            template = "./pdfs/new_req/Archive/Vitamin_d_labcorp_pb.pdf"
        elif test == "Sleep & Stress Hormone Test":
            template = "./pdfs/new_req/Archive/Sleep_&_stress_labcorp_pb.pdf"
        elif test == "Cortisol Test":
            template = "./pdfs/new_req/Archive/Cortisol_labcorp_pb.pdf"
        elif test == "Female Hormone Complete":
            template = "./pdfs/new_req/Archive/Female_hormone_labcorp_pb.pdf"     
        elif test == "Gonorrhea":
            template = "./pdfs/newFive/gonorrhea_labcorp_pb.pdf"   
        elif test == "Trichomoniasis":
            template = "./pdfs/new_req/newFive/trich_labcorp_pb.pdf"
        elif test == "Chlamydia":
            template = "./pdfs/newFive/chlamydia_labcorp_pb.pdf"     
        elif test == "Complete Vitamin & Mineral Panel":
            template = "./pdfs/newFive/vitamin_complete_labcorp_pb.pdf"   
        elif test == "Mycoplasma & Ureaplasma":
            template = "./pdfs/newFive/myco_urea_labcorp_pb.pdf"
        elif test == "Female Hormone Standard":
            template = "./pdfs/new_req/Archive/Ovarian_reserve_labcorp_pb.pdf"
        elif test == "Male Hormone Test":
            template = "./pdfs/new_req/Archive/Male_hormone_labcorp_pb.pdf"
        elif test == "Male Hormone Standard":
            template = "./pdfs/new_req/Archive/Testosterone_labcorp_pb.pdf"
        elif test == "Heavy Metals Test":
            template = "./pdfs/new_req/Archive/Heavy_metals_labcorp_pb.pdf"
        elif test == "HIV P24 Antigen Early Detection":
            template = "./pdfs/new_req/Archive/HIV_early_labcorp_pb.pdf"
        elif test == "Lyme Disease Test":
            template = "./pdfs/new_req/Archive/Lyme_disease_labcorp_pb.pdf"
        elif test == "Indoor and Outdoor Allergy":
            if(region_no == "1"):
                template = "./pdfs/new_req/Archive/Allergy_region_1_pb.pdf"
            elif (region_no == "2"):
                template = "./pdfs/new_req/Archive/Allergy_region_2_pb.pdf"
            elif (region_no == "3"):
                template = "./pdfs/new_req/Archive/Allergy_region_3_pb.pdf"
            elif (region_no == "4"):
                template = "./pdfs/new_req/pb/Allergy_region_4_pb.pdf"
            elif (region_no == "5"):
                template = "./pdfs/new_req/Archive/Allergy_region_5_pb.pdf"
            elif (region_no == "6"):
                template = "./pdfs/new_req/Archive/Allergy_region_6_pb.pdf"
            elif (region_no == "7"):
                template = "./pdfs/new_req/Archive/Allergy_region_7_pb.pdf"
            elif (region_no == "8"):
                template = "./pdfs/new_req/Archive/Allergy_region_8_pb.pdf"
            elif (region_no == "9"):
                template = "./pdfs/new_req/Archive/Allergy_region_9_pb.pdf"
            elif (region_no == "10"):
                template = "./pdfs/new_req/Archive/Allergy_region_10_pb.pdf"
            elif (region_no == "11"):
                template = "./pdfs/new_req/Archive/Allergy_region_11_pb.pdf"
            elif (region_no == "12"):
                template = "./pdfs/new_req/Archive/Allergy_region_12_pb.pdf"
            elif (region_no == "13"):
                template = "./pdfs/new_req/Archive/Allergy_region_13_pb.pdf"
            elif (region_no == "14"):
                template = "./pdfs/new_req/Archive/Allergy_region_14_pb.pdf"
            elif (region_no == "15"):
                template = "./pdfs/new_req/Archive/Allergy_region_15_pb.pdf"
            elif (region_no == "16"):
                template = "./pdfs/new_req/Archive/Allergy_region_16_pb.pdf"
            elif (region_no == "17"):
                template = "./pdfs/new_req/Archive/Allergy_region_17_pb.pdf"
            elif (region_no == "18"):
                template="./pdfs/labcorp_complete_m.pdf"
        else:
              template="./pdfs/labcorp_complete_m.pdf"  
    else:
        if test == "STD Basic":
            template = "./pdfs/labcorp/patient/labcorp-std-cg-patient.pdf"
        elif test == "STD Standard":
            template = "./pdfs/labcorp/patient/labcorp-std-standard-patient.pdf"
        elif test == "STD Complete":
            template = "./pdfs/labcorp/patient/labcorp-std-complete-patient.pdf"
        elif test == "36 Food Allergy Panel":
            template = "./pdfs/labcorp/patient/labcorp-allergies-food-patient.pdf"
        elif test == "Celiac Complete":
            template = "./pdfs/labcorp/patient/labcorp-allergies-celiac-patient.pdf"
        elif test == "Thyroid Test":
            template = "./pdfs/labcorp/patient/labcorp-thyroid-patient.pdf"
        elif test == "Metabolism Test":
            template = "./pdfs/labcorp/patient/labcorp-metabolism-patient.pdf"
        elif test == "Hemoglobin A1C Test":
            template = "./pdfs/labcorp/patient/heartvitaminsleep/labcorp-heart-a1c-patient.pdf"
        elif test == "Cholesterol & Lipids Panel":
            template = "./pdfs/labcorp/patient/heartvitaminsleep/labcorp-heart-lipid-patient.pdf"
        elif test == "Thyroid Standard Panel":
            template =  "./pdfs/new_req/Archive/Thyroid_standard_labcorp_pb.pdf"
        elif test == "Thyroid Complete Panel":
            template =  "./pdfs/new_req/Archive/Thyroid_complete_labcorp_pb.pdf"
        elif test == "Vitamin B Panel":
            template = "./pdfs/labcorp/patient/heartvitaminsleep/labcorp-vitamin-vitb-patient.pdf"
        elif test == "Vitamin D & Inflammation Test":
            template = "./pdfs/labcorp/patient/heartvitaminsleep/labcorp-vitamin-vitd-patient.pdf"
        elif test == "Sleep & Stress Hormone Test":
            template = "./pdfs/labcorp/patient/heartvitaminsleep/labcorp-sleepstress-sleepstress-patient.pdf"
        elif test == "Cortisol Test":
            template = "./pdfs/labcorp/patient/heartvitaminsleep/labcorp-sleepstress-coritosl-patient.pdf"
        elif test == "Female Hormone Complete":
            template = "./pdfs/labcorp/patient/labcorp-femalehormone-patient.pdf"
        elif test == "Female Hormone Standard":
            template = "./pdfs/labcorp/patient/labcorp-fertility-patient.pdf"
        elif test == "Male Hormone Test":
            template = "./pdfs/labcorp/patient/labcorp-malehormone-patient.pdf"
        elif test == "Male Hormone Standard":
            template = "./pdfs/labcorp/patient/labcorp-testosterone-patient.pdf"
        elif test == "Heavy Metals Test":
            template = "./pdfs/labcorp/patient/labcorp-metals-patient.pdf"
        elif test == "Lyme Disease Test":
            template = "./pdfs/labcorp/patient/labcorp-lyme-patient.pdf"
        elif test == "Indoor and Outdoor Allergy":
            if(region_no == "1"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io01-patient.pdf"
            elif (region_no == "2"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io02-patient.pdf"
            elif (region_no == "3"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io03-patient.pdf"
            elif (region_no == "4"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io04-patient.pdf"
            elif (region_no == "5"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io05-patient.pdf"
            elif (region_no == "6"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io06-patient.pdf"
            elif (region_no == "7"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io07-patient.pdf"
            elif (region_no == "8"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io08-patient.pdf"
            elif (region_no == "9"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io09-patient.pdf"
            elif (region_no == "10"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io10-patient.pdf"
            elif (region_no == "11"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io11-patient.pdf"
            elif (region_no == "12"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io12-patient.pdf"
            elif (region_no == "13"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io13-patient.pdf"
            elif (region_no == "14"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io14-patient.pdf"
            elif (region_no == "15"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io15-patient.pdf"
            elif (region_no == "16"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io16-patient.pdf"
            elif (region_no == "17"):
                template = "./pdfs/labcorp/patient/labcorp-allergies-io17-patient.pdf"
            elif (region_no == "18"):
                template="./pdfs/labcorp_complete_m.pdf"
        else:
              template="./pdfs/labcorp_complete_m.pdf"  
        
    if template != "":
        if is_insurance == 1 or (insurance == 1 and test == "Indoor and Outdoor Allergy") or (insurance == 0 and test == "Thyroid Complete Panel") or (insurance == 0 and test == "Thyroid Standard Panel"):
            logger.debug(template)
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFillColorRGB(0, 0, 0)
            can.setFont("Courier", 10)
            can.drawString(160, 378, f"{name}")
            can.drawString(160, 354, f"{dob_month}/{dob_date}/{dob_year}")
            can.drawString(160, 366, sex)
            if len(insurance.split(",")) == 3:
                insurance_arr = insurance.split(",")
                insurance_id = insurance_arr[0]
                insurance_name = insurance_arr[1]
                insurance_group = insurance_arr[2]

                can.drawString(405, 355, insurance_id)
                can.drawString(405, 378, insurance_name)
                can.drawString(406, 331, insurance_group)
            can.save()
    
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            
            existing_pdf = PdfFileReader(open(template, "rb"))
            first_page = PdfFileReader(open(labcorpFirst, "rb"))
            output = PdfFileWriter()
    
            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(first_page.getPage(0))
            output.addPage(page)
    
            outputStream = io.BytesIO()
            # outputStream = open("destination.pdf", "wb")
            output.write(outputStream)
            
            outputStream.seek(0)
            pdf_bytes = outputStream.read()
            outputStream.seek(0)
            pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
    
            connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
            connection.commit()
            cursor = connection.cursor()
            cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
            if (len(list(cursor.fetchall())) > 0):
                logger.debug("existing visit")
                cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
            else:
                cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
            connection.commit()
            connection.close()
    
            # final = convert_from_bytes(pdf_bytes)
            # outputStream.close()
    
            # final_bytes = io.BytesIO()
            # final[0].save(final_bytes, format="JPEG")
    
            # final_bytes.seek(0)
            # files = {
            #     'attachments': ('test.jpg', final_bytes,'image/jpeg')
            # }
            # form_data = {
            #     'faxNumber': fax,
            #     'coverPage': 'false'
            # }
    
            # url = 'https://api.documo.com/v1/faxes'
            # r = requests.post(url, headers=headers, files=files, data=form_data, verify=False)
    
            # return r.json()
            return "Success"
        else:    
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFillColorRGB(0, 0, 0)
            can.setFont("Courier", 8)
    
            # can.drawString(532, 772, "212-530-7891")
    # if     is_insurance != 1:    
    #         can.drawString(376, 777, "✔")
    
            first_name = name.split(" ")[0]
    
            try:
                last_name = name.split(" ")[1]
            except:
                last_name = ""
            can.drawString(160, 653, f"{last_name}, {first_name}")
    
            can.drawString(380, 651, str(dob_month))
            can.drawString(403, 651, str(dob_date))
            can.drawString(418, 651, str(dob_year))
            can.drawString(363, 653, sex)
    
            if len(insurance.split(",")) == 3:
                insurance_arr = insurance.split(",")
                insurance_id = insurance_arr[0]
                insurance_name = insurance_arr[1]
                insurance_group = insurance_arr[2]
    
                can.drawString(160, 531, insurance_id)
                can.drawString(160, 548, insurance_name)
                can.drawString(160, 514, insurance_group)
    
            can.drawString(545, 608, phone)
            can.save()
    
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
    
            existing_pdf = PdfFileReader(open(template, "rb"))
            first_page = PdfFileReader(open(labcorpFirst, "rb"))
            output = PdfFileWriter()
    
            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(first_page.getPage(0))
            output.addPage(page)
    
            outputStream = io.BytesIO()
            # outputStream = open("destination.pdf", "wb")
            output.write(outputStream)
            
            outputStream.seek(0)
    
            pdf_bytes = outputStream.read()
            outputStream.seek(0)
            pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
    
            connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
            connection.commit()
            cursor = connection.cursor()
            cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
            if (len(list(cursor.fetchall())) > 0):
                logger.debug("existing visit")
                data =  cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
            else:
                data = cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
            connection.commit()
            connection.close()
    
    
            # final = convert_from_bytes(pdf_bytes)
            # outputStream.close()
    
            # final_bytes = io.BytesIO()
            # final[0].save(final_bytes, format="JPEG")
    
            # final_bytes.seek(0)
            # files = {
            #     'attachments': ('test.jpg', final_bytes,'image/jpeg')
            # }
            # form_data = {
            #     'faxNumber': fax,
            #     'coverPage': 'false'
            # }
    
            # url = 'https://api.documo.com/v1/faxes'
            # r = requests.post(url, headers=headers, files=files, data=form_data, verify=False)
    
            # return r.json()
            return data
    else:
        return "Failed"
    
  
# generate_quest_pdf("STD Standard", 0, "Maria Bilfeldt", 23, 5, 1991, "mariapiabilfeldt@gmail.com", "5616575152", "F", "12125307891", "", "123456789,Athena,12345")
def generate_empire_pdf(test, is_insurance, name, dob_month, dob_date, dob_year, email, phone, sex, fax, mrn, insurance):
    template = "./pdfs/empire.pdf"
    logger.debug(dob_month)
    if template != "":

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFillColorRGB(0, 0, 0)
        can.setFont("Courier", 10)

        first_name = name.split(" ")[0]

        try:
            last_name = name.split(" ")[1]
        except:
            last_name = ""
        can.drawString(50, 650, f"{last_name}")
        can.drawString(400, 650, f"{first_name}")

        can.drawString(50, 610, f"{dob_month}/{dob_date}/{dob_year}")
        can.drawString(170, 610, sex)
        if len(insurance.split(",")) == 3:
            insurance_arr = insurance.split(",")
            insurance_id = insurance_arr[0]
            insurance_name = insurance_arr[1]
            insurance_group = insurance_arr[2]

            can.drawString(250, 525, insurance_id)
            can.drawString(100, 525, insurance_name)
            can.drawString(100, 510, insurance_group)
        can.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        existing_pdf = PdfFileReader(open(template, "rb"))
        output = PdfFileWriter()

        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        outputStream = io.BytesIO()
        # outputStream = open("destination.pdf", "w+")
        output.write(outputStream)
        
        outputStream.seek(0)
        pdf_bytes = outputStream.read()
        outputStream.seek(0)
        pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
        connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
        connection.commit()
        cursor = connection.cursor()
        cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
        if (len(list(cursor.fetchall())) > 0):
            logger.debug("existing visit")
            cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
        else:
            cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
        connection.commit()
        connection.close()

        return pdf_base64
    else:
        return "Failed"

# def generate_enzo_pdf(test, is_insurance, name, dob_month, dob_date, dob_year, email, phone, sex, fax, mrn, insurance):
#     template = "./pdfs/enzo.pdf"
#     logger.debug(dob_month)
#     if template != "":

#         packet = io.BytesIO()
#         can = canvas.Canvas(packet, pagesize=letter)
#         can.setFillColorRGB(0, 0, 0)
#         can.setFont("Courier", 10)

#         first_name = name.split(" ")[0]

#         try:
#             last_name = name.split(" ")[1]
#         except:
#             last_name = ""
#         can.drawString(50, 690, f"{last_name}")
#         can.drawString(200, 690, f"{first_name}")

#         can.drawString(100, 600, f"{dob_month}/{dob_date}/{dob_year}")
#         can.drawString(30, 610, sex) 
        
#         if len(insurance.split(",")) == 3:
            
#             insurance_arr = insurance.split(",")
#             insurance_id = insurance_arr[0]
#             insurance_name = insurance_arr[1]
#             insurance_group = insurance_arr[2]

#             can.drawString(100, 550, insurance_id)
#             can.drawString(100, 525, insurance_name)
#             can.drawString(100, 570, insurance_group)
#         can.save()

#         packet.seek(0)
#         new_pdf = PdfFileReader(packet)
#         existing_pdf = PdfFileReader(open(template, "rb"))
#         output = PdfFileWriter()

#         page = existing_pdf.getPage(0)
#         page.mergePage(new_pdf.getPage(0))
#         output.addPage(page)
#         outputStream = io.BytesIO()
#         # outputStream = open("destination.pdf", "w+")
#         output.write(outputStream)
        
#         outputStream.seek(0)
#         pdf_bytes = outputStream.read()
#         outputStream.seek(0)
#         pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
#         connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
#         connection.commit()
#         cursor = connection.cursor()
#         cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
#         if (len(list(cursor.fetchall())) > 0):
#             logger.debug("existing visit")
#             cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
#         else:
#             cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
#         connection.commit()
#         connection.close()

#         return pdf_base64
#     else:
#         return "Failed"
    
def generate_northwell_pdf(test, is_insurance, name, dob_month, dob_date, dob_year, email, phone, sex, fax, mrn, insurance):
    template = "./pdfs/northwell.pdf"
    logger.debug(dob_month)
    if template != "":

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFillColorRGB(0, 0, 0)
        can.setFont("Courier", 10)

        first_name = name.split(" ")[0]

        try:
            last_name = name.split(" ")[1]
        except:
            last_name = ""
        can.drawString(100, 600, f"{last_name}")
        can.drawString(200, 600, f"{first_name}")

        can.drawString(90, 580, f"{dob_month}/{dob_date}/{dob_year}")
        can.drawString(200, 580, sex)
        
        if len(insurance.split(",")) == 3:
            insurance_arr = insurance.split(",")
            insurance_id = insurance_arr[0]
            insurance_name = insurance_arr[1]
            insurance_group = insurance_arr[2]

            can.drawString(420, 375, insurance_id)
            can.drawString(100, 375, insurance_name)
            can.drawString(100, 395, insurance_group)

        can.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        existing_pdf = PdfFileReader(open(template, "rb"))
        output = PdfFileWriter()

        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        outputStream = io.BytesIO()
        # outputStream = open("destination.pdf", "w+")
        output.write(outputStream)
        
        outputStream.seek(0)
        pdf_bytes = outputStream.read()
        outputStream.seek(0)
        pdf_base64 =  base64.b64encode(outputStream.getvalue()).decode()
        connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
        connection.commit()
        cursor = connection.cursor()
        cursor.execute(f'select * from fax_forms where mrn="{mrn}"')
        if (len(list(cursor.fetchall())) > 0):
            logger.debug("existing visit")
            cursor.execute(f'update fax_forms set pdf="{pdf_base64}" where mrn="{mrn}"')
        else:
            cursor.execute(f'insert into fax_forms (mrn, pdf) values ("{mrn}", "{pdf_base64}")')
        connection.commit()
        connection.close()

        return pdf_base64
    else:
        return "Failed"