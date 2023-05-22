import smtplib  
import email.utils
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv, io
from email.mime.base import MIMEBase
import pymysql
from datetime import datetime, timedelta
from config import *
from pytz import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

est = timezone('EST')

SENDER = 'nand@joinhelio.com'  
SENDERNAME = 'Next Medical'

USERNAME_SMTP = "AKIAQXYVC547EKFMCXHF"
PASSWORD_SMTP = "BIxfrtJ/H4/rA7JEdYLcnHlVmuHo8V/GYifovCNkwBg9"

HOST = "email-smtp.us-east-2.amazonaws.com"
PORT = 587

#  patients name, address, amount of time spent by ma, date

def send_email(doctor_email, biller_name, biller_email):
    connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    RECIPIENT = biller_email
    BILLER_NAME = biller_name

    cursor.execute(f'select * from visits where doctor_email="{doctor_email}"')

    patients = list(cursor.fetchall())
    print(patients)

    final = [["Patient Name", "Address", "Time Spent by MA (min)", "Date of Visit"]]
    now = datetime.now(est)
    week_back = now - timedelta(days=7)

    for patient in patients:
        t = datetime(patient["visit_year"], patient["visit_month"], patient["visit_date"])

        t = est.localize(t)
        if t >= week_back and patient["visit_status"] != 0:
            final.append([patient["patient_name"], patient["address"], str(patient["visit_duration"]) + " min", str(t.strftime('%m/%d/%Y'))])

    print(final)
    s = io.StringIO()
    csv.writer(s).writerows(final)
    s.seek(0)

    SUBJECT = f'Next Medical Visits for week of {week_back.strftime("%m/%d/%Y")}'
    BODY_TEXT = (
             f'Hi {BILLER_NAME.split(" ")[0]}, See the attached files for the log of this week’s visits from Dr. {patients[0]["doctor_name"]} on Next medical'
            )
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT
    part1 = MIMEText(BODY_TEXT, 'plain')
    msg.attach(part1)
    part = MIMEBase('application', "octet-stream")
    part.set_payload(s.getvalue())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename="patients.csv")
    msg.attach(part)
    try:
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()
        # Display an error message if something goes wrong.
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")

def some_job():
    connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute(f'select * from billers')

    billers = list(cursor.fetchall())

    for i in billers:
        send_email(i["doctor_email"], i["biller_name"], i["biller_email"])


sched = BlockingScheduler({'apscheduler.timezone': 'EST'})
sched.add_job(some_job, 'cron', day_of_week='mon', hour=0, minute=0)
sched.start()