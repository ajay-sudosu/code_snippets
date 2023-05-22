from datetime import date, datetime, timedelta
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red, black

import base64
from io import StringIO, BytesIO
from db_client import *
from pysftp import Connection, CnOpts
import os
import shutil

from pytz import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
tz = timezone('EST')

import pymysql

endpoint = "nextmed-database.crkwdx8kqlsw.us-east-2.rds.amazonaws.com"
username = "admin"
password = "password6969"


cnopts = CnOpts()
cnopts.hostkeys = None

def calculate_age(birthDate): 
    today = date.today() 
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
  
    return age

def parse_datetime(k):
    return k[4] + k[5] + "/" + k[6] + k[7] + "/" + k[0] + k[1] + k[2] + k[3] + " " + k[8] + k[9] + ":" + k[10] + k[11]

def parse_hl7(data):
    final = []
    for i in data.splitlines():
        temp_arr = []
        temp = ""
        for j in i:
            if j == "|":
                if temp != "":
                    temp_arr.append(temp)
                temp = ""
            else:
                temp += j
        if temp != "":
            temp_arr.append(temp)

        final.append(temp_arr)
    return final

def create_pdf_report(data):

    parsed_data = parse_hl7(data)
    para = []
    accession = "NA"
    order_id = "NA"
    patient_name = "NA"
    dob = "NA"
    age = "NA "
    gender = "NA"

    phone = ""
    coll_date = "NA"
    recv_date = "NA"
    first_report_date = "NA"
    final_report_date = "NA"
    print_date="NA"

    test_title = "NA"
    test_name = "NA"
    in_range = "NA"
    out_of_range = "Not Detected"

    for i in parsed_data:
        if i[0] == "PID":
            
            patient_name = i[4].replace("^", ", ")
            dob = i[5][4] + i[5][5] + "/" + i[5][6] + i[5][7] + "/" + i[5][0] + i[5][1] + i[5][2] + i[5][3]
            age = calculate_age(date(int(i[5][0] + i[5][1] + i[5][2] + i[5][3]), int(i[5][4] + i[5][5]), int(i[5][6] + i[5][7])))
            gender = i[6]
            try:
                phone = i[8]
            except:
                True
        elif i[0] == "OBR":
            coll_date = parse_datetime(i[5])[0:10]
            first_report_date = parse_datetime(i[8])
            test_title = i[4].split("^")[1]
            accession = i[3]
            order_id = i[2]
        elif i[0] == "ORC":
            recv_date = parse_datetime(i[5])

        elif i[0] == "OBX":
            test_name = i[3].split("^")[1]
            in_range = i[5]

        elif i[0] == "MSH":
            final_report_date = parse_datetime(i[6])
            print_date = parse_datetime(i[6])

        elif i[0] == "NTE":
            para.append(i[2])

    
    try:
        connection = pymysql.connect(endpoint, user=username, passwd=password, db="nextmed")
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where order_id="{order_id}"')
        visit = list(cursor.fetchall())[0]
        passport_number = visit["passport_number"]
    except:
        passport_number = ""

    pdf_file = BytesIO()
    canvas = Canvas(pdf_file, pagesize=A4)
    canvas.setFont("Courier", 9)

    canvas.drawString(6 * cm, 28.7 * cm, "229 49th Street")
    canvas.drawString(6 * cm, 28.2 * cm, "Brooklyn, NY 11220-1708")
    canvas.drawString(6 * cm, 27.7 * cm, "Tel. (718) 788-3840")
    canvas.drawString(6 * cm, 27.2 * cm, "Fax. (718) 788-3871")
    canvas.drawImage("logo.png", 1 * cm, 27.2 * cm, 4 * cm, 1.8 * cm)

    canvas.setFont("Courier-Bold", 11)
    canvas.drawString(12 * cm, 28.7 * cm, "Fermina M. Mazzella, MD")
    canvas.setFont("Courier", 9)
    canvas.drawString(12 * cm, 28.2 * cm, "Laboratory Director")
    canvas.drawString(12 * cm, 27.7 * cm, "CLIA No: 33D1057336")

    canvas.setFont("Courier-Bold", 10)
    canvas.drawString(1 * cm, 26.2 * cm, "Phys: COHEN, MATTHEW SCOTT")
    canvas.setFont("Courier", 8)
    canvas.drawString(1 * cm, 25.7 * cm, "272 WEST PARK AVE")
    canvas.drawString(1 * cm, 25.2 * cm, "LONG BEACH, NY 11561")
    canvas.drawString(1 * cm, 24.7 * cm, "(516) 543-5000")
    canvas.drawString(1 * cm, 24.2 * cm, "COHEN, MATTHEW SCOTT MD FAAP")

    canvas.setFont("Courier-Bold", 10)
    canvas.drawString(8  * cm, 26.2 * cm, f'Patient: {patient_name}')
    canvas.setFont("Courier", 8)


    canvas.drawString(8 * cm, 25.7 * cm, f'DOB: {dob}      Age: {age}Y      Gender: {gender}')
    if passport_number == "":
        canvas.drawString(8 * cm, 25.2 * cm, f'Phone: {phone}                   Fasting: U')
    else:
        canvas.drawString(8 * cm, 25.2 * cm, f'Passport Number: {passport_number}    Phone: {phone}    Fasting: U')
    canvas.drawString(8 * cm, 24.7 * cm, "Spec#")

    canvas.setFont("Courier-Bold", 10)
    canvas.drawString(1 * cm, 23.2 * cm, f'Accession: {accession}')
    canvas.setFont("Courier", 8)
    canvas.drawString(1 * cm, 22.7 * cm, f'Coll. Date: {coll_date}')
    canvas.drawString(1 * cm, 22.2 * cm, f'Recv. Date: {recv_date}')

    canvas.drawString(8 * cm, 23.2 * cm, f'First Report Date: {first_report_date}')
    canvas.drawString(8 * cm, 22.7 * cm, f'Final Report Date: {final_report_date}')
    canvas.drawString(8 * cm, 22.2 * cm, f'Print Date: {print_date}')

    canvas.setFont("Courier-Bold", 10)

    canvas.drawString(1 * cm, 21.2 * cm, test_name)
    canvas.setFont("Courier", 8)
    canvas.drawString(1 * cm, 20.7 * cm, test_title)

    if "Detected" in in_range:
        out_of_range = "Not Detected"
    else:
        out_of_range = "Negative"

    if in_range == "Detected" or in_range == "Positive":
        canvas.setFillColor(red)
        canvas.setFont("Courier-Bold", 8)
        canvas.drawString(1 * cm, 20.2 * cm, f'Test name: {test_name}       Out Of Range: {in_range}       Reference: {out_of_range}')
    else:
        canvas.setFont("Courier-Bold", 8)
        canvas.drawString(1 * cm, 20.2 * cm, f'Test name: {test_name}       In Range: {in_range}       Reference: {out_of_range}')
    canvas.setFillColor(black)
    canvas.setFont("Courier", 8)

    for i in range(0, len(para)):
        canvas.drawString(1 * cm, (19.2 - (i * 0.4)) * cm, para[i])


    canvas.save()
    pdf_base64 =  "data:application/pdf;base64," + base64.b64encode(pdf_file.getvalue()).decode()

    client = DBClient()
    client.upload_sftp_results(order_id, pdf_base64, test_name)

def job():
    print("RUNNING JOB...")
    with Connection('ftp.wellcom.us',username='NEXTMEDICAL',password ='nx0xO5d!DB%9Md',cnopts=cnopts) as sftp:
        sftp.get_r('/RESULTS/', ".")
    k = os.listdir("./RESULTS")

    for i in k:
        if "HL7" in i:
            t = open("./RESULTS/" + i, "r").read()
            try:
                create_pdf_report(t)
            except Exception as e:
                print(str(e))
    shutil.rmtree("RESULTS")


print("STARTING JOB")
sched = BlockingScheduler({'apscheduler.timezone': 'EST'})
sched.add_job(job, 'cron', minute=30)
sched.start()