import base64
import calendar
import csv
import email.utils
import logging
import math
import smtplib
import time
import uuid
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from random import randint
from urllib.parse import parse_qs
from urllib.parse import urlparse

import json 
import gspread
import pymysql
import requests
import stripe
from exponent_server_sdk import PushClient, PushMessage
from haversine import haversine
from pymysql import NULL
from pysftp import Connection, CnOpts
from pytz import timezone
from reportlab.lib.colors import red, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from twilio.rest import Client
from utils import send_text_message
import mdintegrations
from auth.cognito import signup_user
from config import *
from fax_api import generate_labcorp_pdf, generate_quest_pdf, generate_northwell_pdf, generate_empire_pdf
from functions import get_duration, push_label_to_s3, parse_final_date, get_random_str, calculate_age, get_percentile, \
    calculate_bmi, get_travel_time, get_travel_time1

logger = logging.getLogger("fastapi")

tz = timezone('EST')

quest_data = list(csv.reader(open("quest.csv")))
allergy_data = list(csv.reader(open("questnew.csv")))
covid_quest_data = list(csv.reader(open("covid.csv")))
covid_enzo_data = list(csv.reader(open("covidTest.csv")))
quest_south_data = list(csv.reader(open("questsouth.csv")))
quest_pruned_data = list(csv.reader(open("questpruned.csv")))
quest_sat_data = list(csv.reader(open("questsat.csv")))

application_id = "AC52304A-BB51-423F-9646-5B0E638DB5B5"

api_headers = {'Api-Token': '0a09df9523a0598a5da88e7aa5e3ccfa739c7f26'}

cnopts = CnOpts()
cnopts.hostkeys = None

SENDER = 'team@joinnextmed.com'
SENDERNAME = 'Next Medical'

USERNAME_SMTP = "AKIAQXYVC547EKFMCXHF"
PASSWORD_SMTP = "BIxfrtJ/H4/rA7JEdYLcnHlVmuHo8V/GYifovCNkwBg9"

HOST = "email-smtp.us-east-2.amazonaws.com"
PORT = 587

ZIP_CODES = {
    "new_york": ['10001', '10116', '10121', '10119', '10018', '10123', '10118', '10122', '10120', '10199', '10060',
                 '10011', '10242', '10113', '10036', '10168', '10249', '10110', '10175', '10176', '10173', '10178',
                 '10165', '10174', '10016', '10101', '10112', '10020', '10170', '10169', '10010', '10177', '10166',
                 '10102', '10109', '10114', '10111', '10167', '10019', '10081', '10087', '10172', '10103', '10104',
                 '10017', '10171', '10055', '10107', '10106', '10154', '10105', '10276', '10014', '10152', '10003',
                 '10151', '10150', '10153', '10022', '10155', '07086', '10012', '10069', '10023', '07030', '10009',
                 '10065', '10002', '11109', '07087', '10013', '10021', '10158', '10278', '10044', '11120', '07093',
                 '10282', '07310', '10108', '10117', '10124', '10125', '10126', '10129', '10130', '10131', '10132',
                 '10133', '10138', '10156', '10157', '10159', '10160', '10163', '10164', '10179', '10185', '10203',
                 '10211', '10212', '10213', '10256', '10258', '10259', '10260', '10261', '10265', '10268', '10269',
                 '10272', '10273', '10274', '10275', '10285', '10286', '10007', '10075', '10279', '10162', '10080',
                 '10008', '10090', '10028', '10277', '10038', '10045', '10271', '07307', '07047', '10280', '10006',
                 '11222', '10005', '11101', '10270', '07302', '10128', '10043', '10281', '10024', '10041', '11106',
                 '11251', '10025', '11211', '11242', '07311', '11202', '11243', '11256', '11201', '11102', '07306',
                 '10029', '11249', '11241', '07094', '11104', '10004', '11205', '07304', '07308', '10026', '07096',
                 '11206', '11245', '11103', '10115', '07097', '07303', '07399', '07395', '10035', '07022', '11377',
                 '07010', '10027', '11217', '11105', '11378', '11247', '07020', '11231', '11237', '10037', '11221',
                 '11238', '11216', '10030', '07657', '11370', '10454', '07305', '10031', '11372', '11215', '10039',
                 '10451', '11373', '11213', '10032', '10455', '11379', '07032', '11232', '11225', '11233', '07072',
                 '07650', '11369', '07071', '11371', '07073', '07024', '10474', '07643', '07074', '11385', '10452',
                 '10456', '07660', '11374', '11212', '07031', '11218', '11368', '10459', '11226', '11207', '11220',
                 '11203', '07605', '07070', '07099', '07608', '07002', '10033', '07699', '07105', '07029', '11219',
                 '10040', '11375', '10453', '11421', '07606', '10473', '10457', '11208', '11356', '07075', '10472',
                 '07604', '07603', '10460', '11351', '11416', '11354', '11367', '11204', '11230', '07104', '11210',
                 '10034', '11352', '11355', '11209', '07109', '07057', '11415', '11236', '11424', '11228', '07101',
                 '07184', '07188', '07189', '07191', '07192', '07193', '07195', '07198', '07199', '07102', '11418',
                 '07175', '11380', '11417', '11381', '11386', '07014', '07632', '07666', '11239', '10468', '07114',
                 '07602', '07631', '07601', '10462', '07110', '10458', '07644', '10463', '11357', '07055', '11419',
                 '11414', '10301', '07107', '11252', '10310', '10461', '11435', '07103', '11358', '11214', '11365',
                 '07026', '11420', '11234', '11229', '11223', '11431', '11405', '11425', '11439', '11451', '11499',
                 '07003', '10467', '11366', '07108', '11432', '07012', '07201', '10465', '07607', '07019', '07017',
                 '10304', '10302', '10313', '10471', '10305', '10469', '07015', '11360', '07112', '07662', '11433',
                 '07028', '07018', '11436', '07670', '07011', '11359', '11361', '11235', '07663', '07621', '11224',
                 '07206', '10303', '11423', '07106', '07042', '10475', '07661', '07013', '07407', '07111', '07051',
                 '11364', '10466', '07043', '10470', '07646', '11434', '10705', '07050', '07207', '11412', '07205',
                 '11427', '07503', '07208', '10464', '10311', '11430', '11363', '07626', '11693', '07513', '11428',
                 '07202', '10702', '07628', '07504', '11022', '10550', '11362', '11429', '11437', '07079', '10314',
                 '10704', '10551', '07652', '07044', '07653', '11411', '11695', '11426', '11023', '07009', '11024',
                 '11413', '07627', '07052', '11697', '07040', '10553', '07649', '11694', '07410', '11021', '07501',
                 '11027', '07514', '10803', '11026', '07641', '10306', '07509', '07510', '07511', '07533', '07543',
                 '07544', '07083', '07424', '07505', '11005', '11004', '11422', '11020', '10552', '07620', '11692',
                 '10805', '07524', '10701', '11001', '11002', '07624', '07522', '07204', '07088', '07203', '11042',
                 '07502', '07630', '11096', '10703', '10708', '11003', '07021', '10802', '07512', '07036', '10308',
                 '07007', '10801', '07452', '11691', '11690', '07507', '07041', '11580', '11582', '07538', '07033',
                 '11581', '11051', '11052', '11053', '11054', '11055', '11030', '11516', '11040', '07640', '07506',
                 '07006', '07676', '10710', '11050', '07068', '07648', '07451', '07450', '07008', '11598', '10707',
                 '11559', '11010', '10709', '10312', '07016', '10804', '11557', '07078', '07508', '07039', '11565',
                 '07081', '10706', '07065', '10538', '07642', '07675', '11509', '07647', '07004', '07423', '11563',
                 '11507', '07064', '11531', '07001', '11576', '10964', '11596', '07027', '07432', '11552', '11501',
                 '07470', '11577', '11518', '11530', '07474', '07066', '10309', '10983', '10976', '07077', '10522',
                 '07902', '07481', '07999', '07901', '07463', '11547', '10543', '07091', '07677', '07090', '11579',
                 '11570', '10583', '07092', '07058', '10502', '11571', '11548', '07656', '11550', '11551', '07067',
                 '10503', '07936', '11514', '11599', '07035', '11572', '11558', '10968', '07095', '07440', '07401',
                 '10530', '07076', '11549', '08830', '10962', '07458', '10307', '07645', '07417', '07932', '10533',
                 '11542', '11568', '10528', '11553', '11555', '11556', '11510', '07928', '10965', '08861', '07974',
                 '11561', '10606', '11590', '07023', '11545', '07034', '11575', '07082', '08862', '10607', '10913',
                 '10605', '08863', '07444', '07940', '07732', '10580', '07734', '07045', '07054', '11520', '07446',
                 '07922', '07758', '07062', '07981', '10601', '08820', '11560', '07436', '10602', '07061', '11554',
                 '10610', '07442', '11569', '07718', '10523', '07961', '08840', '08832', '10960', '07457', '07737',
                 '10954', '07935', '11753', '07735', '11566', '11853', '10994', '10603', '10591', '07752', '07060',
                 '07716', '07730', '08879', '07430', '11732', '08837', '07069', '07927', '11710', '10577', '11802',
                 '11815', '11765', '11801', '07420', '10604'],
    "miami": ['33301', '33348', '33355', '33394', '33302', '33303', '33307', '33310', '33318', '33320', '33335',
              '33338', '33339', '33340', '33345', '33346', '33349', '33304', '33316', '33305', '33315', '33306',
              '33311', '33312', '33004', '33334', '33308', '33309', '33317', '33313', '33020', '33314', '33019',
              '33359', '33329', '33093', '33097', '33319', '33022', '33081', '33082', '33083', '33084', '33060',
              '33388', '33021', '33061', '33077', '33068', '33337', '33069', '33336', '33324', '33322', '33062',
              '33066', '33328', '33024', '33075', '33008', '33009', '33351', '33023', '33063', '33321', '33064',
              '33074', '33180', '33280', '33179', '33071', '33325', '33072', '33026', '33160', '33073', '33323',
              '33442', '33330', '33065', '33441', '33025', '33169', '33162', '33443', '33056', '33067', '33055',
              '33028', '33326', '33154', '33181', '33486', '33331', '33433', '33432', '33076', '33161', '33027',
              '33168', '33481', '33497', '33499', '33427', '33429', '33428', '33261', '33054', '33167', '33015',
              '33488', '33431', '33327', '33332', '33434', '33141', '33014', '33138', '33150', '33029', '33147',
              '33487', '33496', '33498', '33013', '33002', '33016', '33011', '33017', '33140', '33012', '33137',
              '33127', '33018', '33142', '33166', '33010', '33484', '33445', '33446', '33444', '33139', '33132',
              '33136', '33482', '33448', '33483', '33128', '33151', '33152', '33153', '33163', '33164', '33101',
              '33102', '33111', '33112', '33116', '33119', '33125', '33188', '33195', '33197', '33238', '33239',
              '33242', '33243', '33245', '33247', '33257', '33265', '33266', '33269', '33299', '33231', '33122',
              '33131', '33109', '33130', '33198', '33135', '33126', '33129', '33178', '33206', '33191', '33145',
              '33255', '33192', '33437', '33134', '33234', '33172', '33473', '33144', '33222', '33133', '33435',
              '33436', '33474', '33424', '33425', '33426', '33472', '33149', '33174', '33155', '33124', '33114',
              '33146', '33182', '33233', '33199', '33165', '33184', '33143', '33462', '33175', '33173', '33256',
              '33283', '33296', '33463', '33467', '33194', '33156', '33449', '33183', '33461', '33464', '33465',
              '33466', '33460', '33185', '33454', '33176', '33158', '33193', '33106', '33414', '33186', '33415',
              '33413', '33406', '33157', '33405', '33480']}

stripe.api_key = STRIPE_API_KEY

SEX_MALE = 0
SEX_FEMALE = 1


def get_upper_bound(k):
    k = int(k / 100)

    if k % 2 == 0:
        return (k + 2) * 100
    else:
        return (k + 1) * 100


def process(k):
    final = ""
    for i in k.lower():
        if i.isalpha() or i.isdigit():
            final += i
    return final


def get_address_details(address):
    try:
        request_str = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}'
        r = requests.get(request_str)
        x = r.json()
        city = "New York"
        state = "NY"

        for i in x["results"][0]["address_components"]:
            if "locality" in i["types"] or "sublocality" in i["types"] or "administrative_area_level_3" in i[
                "types"] or "administrative_area_level_2" in i["types"]:
                city = i["short_name"]
                break

        for j in x["results"][0]["address_components"]:

            if ["administrative_area_level_1"] in j["types"]:
                state = j["short_name"]
                break

        return {"city": city, "state": state, "address": x["results"][0]["formatted_address"].split(", ")[0]}
    except:
        return {"city": "NYC", "state": "NY", "address": "NYC, NY, USA"}


def parse_time(t):
    try:
        t = str(t)
        if t == "2400":
            return "12:00 AM"
        if len(t) == 4:
            final = t[0] + t[1] + ":" + t[2] + t[3]
        else:
            final = t[0] + ":" + t[1] + t[2]

        try:
            d = datetime.strptime(final, "%H:%M")
            return d.strftime("%I:%M %p")
        except:
            return final

    except:
        return "NA"


def convert_time(a, b):
    num_mutiples = int((b + (a % 100)) / 60)
    a += num_mutiples * 40 + b
    return a


def splice_intervals(k, current_time, end_time):
    final = []
    if k[2] <= current_time and k[2] + 200 >= current_time:
        pass
    else:
        if k[2] < end_time:
            final.append([k[0], k[1], k[2], k[2] + 200, k[4]])

    first = int((k[2] + 200) / 100) * 100

    if first / 100 % 2 == 1:
        first -= 100
    last = (int(k[3] / 100) * 100) + 1
    for i in range(first, last, 200):
        if i <= current_time and i + 200 >= current_time:
            pass
        else:
            if i < end_time:
                final.append([k[0], k[1], i, i + 200, k[4]])
    return final


def get_nurse_time_interval(a, b):
    if int(a / 100) % 2 == 1:
        return parse_time((int(a / 100) - 1) * 100) + " - " + parse_time((int(b / 100) - 1) * 100)
    else:
        return parse_time(int(a / 100) * 100) + " - " + parse_time(int(b / 100) * 100)


class DBClient:
    def __init__(self):
        self.endpoint = DB_ENDPOINT
        self.database = DB_NAME
        self.username = DB_USERNAME
        self.password = DB_PASSWORD
        self.connection = pymysql.connect(
            host=self.endpoint, user=self.username, passwd=self.password, db=self.database
        )

    def upload_sftp(self, mrn, ssn, insurance_id, insurance_name, order_id, timestamp, accession_number):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')

        is_send = False

        visit = list(cursor.fetchall())[0]
        tests = visit["consumer_notes"]

        patient_id = randint(10000000, 99999999)

        name_arr = visit["patient_name"].split(" ")
        first_name = name_arr[0]
        if len(name_arr) == 1:
            last_name = ""
        else:
            last_name = name_arr[len(name_arr) - 1]

        address_details = get_address_details(visit["address"])
        dob = str(visit["dob_year"])
        if int(visit["dob_month"]) < 10:
            dob += "0"
        dob += str(visit["dob_month"])

        if int(visit["dob_date"]) < 10:
            dob += "0"
        dob += str(visit["dob_date"])

        if visit["sex"] == 0:
            gender = "Male"
        elif visit["sex"] == 1:
            gender = "Female"
        else:
            gender = "Other"

        order = f"""MSH|^~\\&|CTRON|21088|NEXTMEDICAL|21088|{timestamp}||ORM^O01|{order_id}|T|2.3|
                PID|1|{patient_id}||{accession_number}|{last_name}^{first_name}^||{dob}|{gender}|||{address_details["address"]}^^{address_details["city"]}^{address_details["state"]}^{visit["zip_code"]}||{visit["phone"]}||||||{ssn}|||| 
                PV1|1||||||1740410463^SEROTA^MARC|||||||||||
                IN1|1||{insurance_id}|{insurance_name}||||||||||||{last_name}^{first_name}^|1|19711104|9071 E. Mississippi Ave. Unit 6C^^Denver^CO||||||||||||||||||||||||||||T|
                GT1|1||{last_name}^{first_name}^||9071 E. Mississippi Ave. Unit 6C^^Denver^CO^80247|2126655892||19711104|{gender}||1|000000111 ORC|NW|{order_id}|||||||{timestamp}|||1740410463^SEROTA^MARC|"""

        for i in TEST_CODES:
            if i in tests:
                is_send = True
                for j in TEST_CODES[i]:
                    if "HIV" in j and visit["is_hiv"] == 0:
                        pass
                    else:
                        order += f"""\nOBR|1|{order_id}||{j}|||{timestamp}|||||||||1740410463^SEROTA^MARC|||||||||||1
                                    DG1|1|I10|Z11.59|(Idiopathic) normal pressure hydrocephalus|"""

        if is_send == True:
            with Connection('ftp.wellcom.us', username='NEXTMEDICAL', password='nx0xO5d!DB%9Md', cnopts=cnopts) as sftp:
                orders_dir = sftp.listdir('/ORDERS')
                file_name = str(len(orders_dir) - 2) + ".HL7"
                f = sftp.open(f'/ORDERS/{file_name}', 'wb')
                f.write(order)

    def give_feedback(self, mrn, recommend, alternative, friendly, convenient, comments, non_covid, future_tests):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(f'select * from visits where mrn="{mrn}";')

        if list(cursor.fetchall()) == []:
            return {"status": "failed", "error": "MRN does not exist."}

        cursor.execute(f'select * from feedback where mrn="{mrn}";')

        if list(cursor.fetchall()) != []:
            return {"status": "failed", "error": "This form has already been filled."}

        query = (
            f'insert into feedback (mrn, recommend, alternative, friendly, convenient, comments, non_covid, future_tests) values ("{mrn}", {recommend}, "{alternative}", {friendly}, {convenient}, "{comments}", "{non_covid}", "{future_tests}");')

        cursor.execute(query)
        self.connection.commit()

        return {"status": "success"}

    def send_feedback(self, recommend, alternative, comments, future_tests,email,name,current_time):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        mrn = get_random_str(8)
        rating = int(recommend)
        query = (
            f'insert into feedback (mrn, recommend, alternative, comments, future_tests ,email ,name) values ("{mrn}","{recommend}", "{alternative}","{comments}","{future_tests}","{email}","{name}");')
        cursor.execute(query)
        if rating > 5 : 
            self.send_patient_feedback_email(
                              recommend, alternative, comments, future_tests)
        else:
            self.send_patient_feedback_bad_email(
                              recommend, alternative, comments, future_tests,name,email,current_time)   
        self.connection.commit()
        return {"status": "success"}

    def get_lab_locations(self, zip_code, is_covid, is_insurance, test_name):
        try:
            spaceless_zip_code = str(zip_code).replace(' ', '')
            if len(str(spaceless_zip_code)) < 5 or len(str(spaceless_zip_code)) > 10:
                raise Exception('Invalid Zipcode')

            if not is_covid:
                if test_name == "Indoor and Outdoor Allergy":
                    final_data = allergy_data
                elif test_name == "Quest":
                    final_data = quest_south_data
                elif test_name == "insurance":
                    final_data = quest_south_data
                elif test_name == "saturday":
                    final_data = quest_sat_data
                else:
                    final_data = quest_data
            elif (is_covid and test_name == "36 Hour RT-PCR") or (is_covid and test_name == "24 Hour RT-PCR"):
                final_data = covid_enzo_data
            else:
                final_data = covid_quest_data

            api_key = 'AIzaSyAe7nmOwtSLsOdfYwJ_ns3p1krP0h97rPE'
            location_data = requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?address={spaceless_zip_code}&key={api_key}"
            )
            location_data = location_data.json()
            if len(location_data.get('results', [])) == 0:
                raise Exception('No results were found against this zipcode')
            location = location_data.get("results", [])[0].get("geometry", {}).get("location")
            final = []
            isIOTest = "false"
            if test_name == "Indoor and Outdoor Allergy":
                isIOTest = "true"
            for lab in final_data[1::]:
                temp = {}
                temp["store_no"] = lab[0]
                temp["name"] = lab[1]
                temp["lat"] = lab[2]
                temp["long"] = lab[3]
                temp["address"] = lab[4]
                temp["lab_fax"] = str(lab[11])
                temp["times"] = lab[12]
                temp["photo_reference"] = lab[20]
                temp["distance"] = haversine(
                    (location["lat"], location["lng"]), (float(lab[2]), float(lab[3])))
                if 21 < len(lab):
                    temp["region_no"] = lab[21]
                if is_insurance or "labcorp" not in lab[1].lower():
                    if isIOTest == "true" and lab[21] != "99":
                        final.append(temp)
                    elif isIOTest == "false":
                        final.append(temp)
            final = sorted(final, key=lambda x: x["distance"])
            return {"status": "success", "data": final[0:5]}
        except Exception as e:
            return {"status": "failure", "data": str(e)}

    def get_gen_pid_data(self,pid):
        f = open('gen_pid.json')
        temp = {}
        data = json.load(f)
        for i in data['pids']:
            if i["pid"] == pid:
                temp= i
                break
        return {"status":"success","data":temp}  


    def sendbird_login(self, user_id):
        response = requests.get(
            f'https://api-{application_id}.sendbird.com/v3/users/{user_id}', headers=api_headers)
        result = response.json()

        if 'access_token' in result:
            return {"status": "success", "access_token": result["access_token"]}
        else:

            cursor = self.connection.cursor(pymysql.cursors.DictCursor)

            cursor.execute(
                f'select * from visits where email="{user_id}" and is_family=0;')

            visits = list(cursor.fetchall())

            if visits == []:
                nickname = user_id.split("@")[0]
            else:
                nickname = visits[0]["patient_name"]
            req_data1 = {
                "user_id": user_id,
                "issue_access_token": True,
                "nickname": nickname,
                "profile_url": "",
            }
            response1 = requests.post(
                f'https://api-{application_id}.sendbird.com/v3/users', headers=api_headers, data=json.dumps(req_data1))
            result1 = response1.json()

            req_data2 = {
                "user_ids": [user_id, "081631"],
                "name": f'Marc Serota, {nickname}'
            }
            response2 = requests.post(
                f'https://api-{application_id}.sendbird.com/v3/group_channels', headers=api_headers,
                data=json.dumps(req_data2))
            result2 = response2.json()
            return {"status": "success", "access_token": result1["access_token"]}

    def get_feedback(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(f'select * from feedback;')

        feedback = list(cursor.fetchall())

        for i in range(0, len(feedback)):
            cursor.execute(
                f'select * from visits where mrn="{feedback[i]["mrn"]}"')
            visit = list(cursor.fetchall())

            if visit != []:
                cursor.execute(
                    f'select * from nurses where email="{visit[0]["nurse_email"]}"')
                nurse = list(cursor.fetchall())
                if nurse != []:
                    feedback[i]["nurse_name"] = nurse[0]["name"]
                feedback[i]["name"] = visit[0]["patient_name"]
                feedback[i]["nurse"] = visit[0]["nurse_email"]
                feedback[i]["apt_date"] = f'{visit[0]["visit_month"]}/{visit[0]["visit_date"]}/{visit[0]["visit_year"]}'
                feedback[i]["email"] = visit[0]["email"]

        self.connection.commit()
        return feedback

    def get_patient_feedback(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from feedback;')
        feedback = list(cursor.fetchall())
        self.connection.commit()
        return feedback
    def get_patient_question(self,mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from question where mrn="{mrn}";')
        feedback = list(cursor.fetchall())
        self.connection.commit()
        return feedback

    def get_schedule(self, visit_date, visit_month, visit_year, location):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from nurses where location="{location}";')
        nurses = list(cursor.fetchall())

        final = ""
        for i in range(0, len(nurses)):
            final += f'MA #{i + 1} ({nurses[i]["name"]})'
            query = f'select * from visits where location="{location}" and nurse_email="{nurses[i]["email"]}" and visit_date={visit_date} and visit_month={visit_month} and visit_year={visit_year}'
            cursor.execute(query)
            visits = list(cursor.fetchall())
            visits = sorted(visits, key=lambda x: x["nurse_time"])

            for j in range(0, len(visits)):
                if visits[j]["apartment_number"] != "":
                    apartment_number = ", apartment: " + \
                                       visits[j]["apartment_number"]
                else:
                    apartment_number = ""
                final += f'\n{j + 1}. {parse_time(visits[j]["nurse_time"])} - {visits[j]["patient_name"]} - {visits[j]["address"]}{apartment_number} ({visits[j]["phone"]}) ({visits[j]["consumer_notes"]})'
            if len(visits) == 0:
                final += f'\nNo visits.'

            final += f'\n'
            final += f'\n'
        return {"status": "success", "data": final}

    def send_email_on_booking(self, city, date, time, options, admin_email):
        city = city.replace("_", " ").title()
        SUBJECT = f'New Next Medical Patient Booking'
        RECIPIENT = admin_email
        BODY_TEXT = (
            f'Hi Rob! A new Next-Medical patient has been booked. Check below for details.\nLocation: {city}\nSelected Tests: {options}'
        )
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'plain')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_email_on_booking_new(self, city, date, time, options, admin_email, path, price, name):
        city = city.replace("_", " ").title()
        SUBJECT = f'New Next Medical Patient Booking'
        RECIPIENT = admin_email
        BODY_TEXT = (
            f'Hi {name}! A new Next-Medical patient has been booked. Check below for details.\nLocation: {city}\nUrl: {path}\nTotal Price: {price}\nSelected Tests: {options}'
        )
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'plain')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_auto_upload_email(self, name, admin_email):
        SUBJECT = f'New Next Medical Patient Auto Upload'
        RECIPIENT = admin_email
        BODY_TEXT = (
            f'Hi Veer! Results have been automatically uploaded for {name}.'
        )
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'plain')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_patient_email(self, patient_email, name, date, time, address):
        SUBJECT = f'Next Medical Appointment Confirmation'
        RECIPIENT = patient_email
        BODY_TEXT = get_html(0, name, date, time, "", address)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_drchrono_email(self, data):
        SUBJECT = f'Next Medical Appointment Confirmation'
        RECIPIENT = "team@joinnextmed.com"
        BODY_TEXT = get_drchrono_add(data)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_klaviyo_track_request(self, email, name, phone_number, item_name, value, is_insurance, test_type, address,
                                   insuranceAmt, mrn):

        url = "https://a.klaviyo.com/api/track"

        val = float(value) / 100

        val = math.ceil(val * 100) / 100

        test_name = item_name
        if test_type.lower() == "std":
            if item_name.lower() == "STD Basic":
                test_name = "Basic Health Test"
            elif item_name.lower() == "std standard":
                test_name = "Standard Health Test"
            else:
                test_name = "Complete Health Test"

        data = {
            "token": "WxSAWz",
            "event": "Ordered Product",
            "customer_properties": {
                "$email": email,
                "$phone_number": str(phone_number),
                "name": name,
                "insurance": is_insurance,
                "item_name": test_name,
                "$value": val,
                "item_type": test_type,
                "location": address,
                "address": address,
                "insurancePrice": math.ceil(insuranceAmt * 100) / 100,
                "testPrice": val - int(insuranceAmt),
                "totalPrice": val,
                "mrn": mrn,
            },
            # "properties": {
            #     "item_name": item_name,
            #     "$value": float(value) / 100,
            #     "item_type": test_type,
            #     "location": address,
            # }
        }

        s = json.dumps(data)
        encoded_string = base64.b64encode(s.encode('utf-8'))

        querystring = {"data": encoded_string}

        headers = {"Accept": "text/html"}

        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        print(response.text, data)

    def send_klaviyo_post_track_request(self, email, name, value):

        url = "https://a.klaviyo.com/api/track"

        val = float(value) / 100

        val = math.ceil(val * 100) / 100

        data = {
            "token": "WxSAWz",
            "event": "Ordered Product",
            "customer_properties": {
                "$email": email
            },
            "properties": {
                "item_name": name,
                "$value": val
            }
        }

        s = json.dumps(data)
        encoded_string = base64.b64encode(s.encode('utf-8'))

        querystring = {"data": encoded_string}

        headers = {"Accept": "text/html"}

        response = requests.request(
            "POST", url, headers=headers, params=querystring)

        print(response.text, data)

    def send_klaviyo_results_request(self, email, name, phone_number, item_name, mrn):

        url = "https://a.klaviyo.com/api/track"
        test_name = item_name

        data = {
            "token": "WxSAWz",
            "event": "Delivered",
            "customer_properties": {
                "$email": email,
                "$phone_number": str(phone_number),
                "name": name,
                "insurance": is_insurance,
                "item_name": test_name,
                "mrn": mrn,
            },
        }

        s = json.dumps(data)
        encoded_string = base64.b64encode(s.encode('utf-8'))

        querystring = {"data": encoded_string}

        headers = {"Accept": "text/html"}

        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        print(response.text, data)

    def send_feedback_email(self, patient_email, name, mrn):
        SUBJECT = f'Next Medical Feedback'
        RECIPIENT = patient_email
        BODY_TEXT = get_html(1, name, "", "", mrn)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_patient_feedback_email(self, recommend, alternative, comments, future_tests):
        SUBJECT = f'Next Medical Feedback'
        RECIPIENT = "team@joinnextmed.com"
        BODY_TEXT = get_html_patient_feedback(
            recommend, alternative, comments, future_tests)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass
        
        

    def send_patient_failed_order_email(self,patient_id):
        SUBJECT = f'LAB ORDER FAILED - PATIENT: {patient_id}'
        RECIPIENT = "team@joinnextmed.com"
        BODY_TEXT = get_html_patient_failed_laborder()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass
        
        
    def send_patient_feedback_bad_email(self, recommend, alternative, comments, future_tests,name , Patientemail,current_time):
        SUBJECT = f'Bad Review'
        RECIPIENT = "team@joinnextmed.com"
        BODY_TEXT = get_html_patient_bad_feedback(
            recommend, alternative, comments, future_tests ,name,Patientemail,time)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_subscription_patient_email(self, email, type):
        SUBJECT = f'Next Medical Subscription'
        RECIPIENT = "robert@joinnextmed.com"
        BODY_TEXT = get_html_patient_subscription(email, type)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def confirmation_order_email(self, emailaddress, name, test):
        SUBJECT = f'Next Medical Comfirmation Order'
        RECIPIENT = emailaddress
        BODY_TEXT = send_confirmation_order(name, test)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_refunded_email(self, patient_email, name, date):
        SUBJECT = f'Next Medical Feedback'
        RECIPIENT = patient_email
        BODY_TEXT = get_html_refunded(name, date)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_results_email(self, patient_email, name):
        SUBJECT = f'Next Medical Test Results'
        RECIPIENT = patient_email
        BODY_TEXT = get_html(2, name, "", "", "")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_doctor_notes_email(self, patient_email, name):
        SUBJECT = f'Test Results Update'
        RECIPIENT = patient_email
        BODY_TEXT = get_html_doctor_note(name)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def send_on_the_way_email(self, patient_email, name, mrn):
        SUBJECT = f'Test Results Update'
        RECIPIENT = patient_email
        BODY_TEXT = get_html_on_the_way(name, mrn)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
        msg['To'] = RECIPIENT
        part1 = MIMEText(BODY_TEXT, 'html')
        msg.attach(part1)
        try:
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            server.close()
        except Exception as e:
            pass

    def update_admins(self, admins):
        cursor = self.connection.cursor()
        cursor.execute("delete from admins where 1=1;")

        for i in admins:
            cursor.execute(f'insert into admins (email) values ("{i[0]}")')
            try:
                signup_user(i[0], i[1])
            except Exception as e:
                pass
                continue

        self.connection.commit()

    def add_biller(self, doctor_email, biller_email, biller_name):
        cursor = self.connection.cursor()
        cursor.execute(
            f'select * from billers where doctor_email="{doctor_email}"')
        if list(cursor.fetchall()) == []:
            cursor.execute(
                f'insert into billers (doctor_email, biller_email, biller_name) values ("{doctor_email}", "{biller_email}", "{biller_name}");')

        else:
            cursor.execute(
                f'update billers set biller_email="{biller_email}", biller_name="{biller_name}" where doctor_email="{doctor_email}";')
        self.connection.commit()

    def get_biller(self, doctor_email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select * from billers where doctor_email="{doctor_email}"')

        k = list(cursor.fetchall())

        if k == []:
            return {"doctor_email": doctor_email, "biller_name": "", "biller_email": ""}
        else:
            return k[0]

    def verify_login(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from admins where email="{email}"')

        admin = list(cursor.fetchall())

        if admin == []:
            cursor.execute(f'select * from doctors where email="{email}"')
            doctor = list(cursor.fetchall())
            if doctor == []:
                return {"status": "success", "type": "invalid"}
            else:

                if doctor[0]["type"] == 0:
                    return {"status": "success", "type": "doctor", "admin": doctor[0]["admin"]}
                elif doctor[0]["type"] == 1:
                    return {"status": "success", "type": "staff", "admin": doctor[0]["admin"]}
                elif doctor[0]["type"] == 2:
                    return {"status": "success", "type": "customer_service", "admin": doctor[0]["admin"]}
                else:
                    return {"status": "success", "type": "admin", "admin": doctor[0]["admin"]}
        else:
            cursor.execute(
                f'select * from subscriptions where email="{email}"')
            sub = list(cursor.fetchall())
            return {"status": "success", "type": "admin", "item_id": "", "sub_id": "", "admin": email}

    def log_subscription(self, email, item_id, sub_id):
        cursor = self.connection.cursor()
        cursor.execute(
            f'insert into subscriptions (email, item_id, sub_id) values ("{email}", "{item_id}", "{sub_id}");')
        self.connection.commit()

    def get_subscription_id(self, email):
        cursor = self.connection.cursor()
        cursor.execute(f'select * from subscriptions where email="{email}"')
        item = list(cursor.fetchall())
        return item[0][1]

    def send_message(self, phone):
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        final_phone = "+1"
        for i in phone:
            if i.isnumeric() == True:
                final_phone += i

        sms = "Click the following link to learn more about your visit: https://joinnextmed.com/"

        message = twilio_client.messages.create(
            body=sms,
            from_='+18454069635',
            to='+1' + str(phone))

    def send_patient_message(self, name, doctor, phone, message_from):
        first_name = name.split()[0]
        final_phone = "+1"
        for i in phone:
            if i.isnumeric() == True:
                final_phone += i
        if message_from == "result":
            sms = f'Hi {first_name},\nResults from your Next Medical visit have been uploaded. Please visit www.joinnextmed.com/login to view them.'
        elif message_from == "checkout_with_insurance":
            sms = f"NEXT MEDICAL WEIGHT LOSS CONFIRMATION AND IMPORTANT INFO:\n\n\n1. Complete your health including why you are interested in the program, your important health data, and your insurance information. By completing this, you will begin the program.\n\n2. Receive your lab order and get tested once you see that your order is complete in the user portal.\n\n3. Get your results and chat with a doctor who will determine your eligibility for weight loss treatment based on your insurance coverage, lab testing, and medical profile.\n\nBegin your weight loss journey!\n\nIf you have any questions, please email us at team@joinnextmed.com and we will get back to you shortly."
        elif message_from == "checkout_without_insurance":
            sms = f"NEXT MEDICAL BOOKING CONFIRMATION AND IMPORTANT INFO:\n\n\n1. If you have not already, fill out your intake form in your profile at joinnextmed.com/login. You will not be tested until you complete this process.\n\n2. Your visit begins with comprehensive testing at your chosen lab, followed by detailed results, post-testing treatment and consultation under the care of Dr. Marc Serota's medical team.\n\nIf you have any questions, please email us at team@joinnextmed.com or call 212-530-7870 and we will get back to you shortly."
        elif message_from == "checkout_with_home":
            sms = f"NEXT MEDICAL BOOKING CONFIRMATION AND IMPORTANT INFO:\n\n\n1. If you have not already, fill out your intake form in your profile at joinnextmed.com/login. You will not be tested until you complete this process.\n\n2. You chose to use insurance for lab processing. Please fill in your insurance information on the intake form and present your insurance card to your nurse when he or she arrives. Failure to do so could lead to high out-of-pocket costs.\n\n3. Your visit begins with comprehensive testing at your home or office, followed by detailed results, post-testing treatment and consultation under the care of Dr. Marc Serota's medical team\n\nIf you have any questions, please email us at team@joinnextmed.com or call 212-530-7870 and we will get back to you shortly."
        else:
            sms = f'Hi {first_name},\nYour doctor, {doctor} has sent you a message. You can view it and respond at https://joinnextmed.com/messages .'

        try:
            send_text_message(phone, sms)
        except Exception as e:
            logger.exception(e)

    def get_nurse_email(self, doctor_email):
        nurse_email_overrides = {"nand@joinhelio.com": "veer@joinnextmed.com"}
        return nurse_email_overrides.get(doctor_email, DEFAULT_NURSE_EMAIL)

    # def __del__(self):
    #     self.connection.commit()
    #     self.connection.close()

    def create_nurse(self, email, name, address, phone, doctor_email, city):
    
        cursor = self.connection.cursor()
        x = (
            f'insert into nurses (email, name, phone, address, image, doctor_email, location, lat, lon, monday_start, monday_end, tuesday_start, tuesday_end, wednesday_start, wednesday_end, thursday_start, thursday_end, friday_start, friday_end, saturday_start, saturday_end, sunday_start, sunday_end, token) values ('
            f'"{email}", "{name}", "{phone}", "{address}", "", "{doctor_email}", "{city}", 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, "");')

        cursor.execute(x)
        self.connection.commit()
        
    def create_question(self, question, answer, mrn,case_id,md_id,pharmacy):
        cursor = self.connection.cursor()
        x = (
            f'insert into question (questions, answer, mrn , case_id ,md_id,pharmacy_id) values ('
            f'"{question}", "{answer}", "{mrn}","{case_id}","{md_id}","{pharmacy}");')
        cursor.execute(x)
        self.connection.commit()

    def update_token(self, email, token):
        cursor = self.connection.cursor()

        x = (f'update nurses\nset token = "{token}"\nwhere email="{email}"')
        cursor.execute(x)
        self.connection.commit()

        cursor.execute(f'select * from nurses where email="{email}"')

    def update_tests_algo(self, mrn, strep, flu, covid):
        cursor = self.connection.cursor()

        if strep == 1:
            x = f'update visits\nset strep = {strep}\nwhere mrn = "{mrn}";'
            cursor.execute(x)
        if flu == 1:
            x = f'update visits\nset flu = {flu}\nwhere mrn = "{mrn}";'
            cursor.execute(x)
        if covid == 1:
            x = f'update visits\nset covid = {covid}\nwhere mrn = "{mrn}";'
            cursor.execute(x)

        self.connection.commit()

    def create_cart(self, email):
        cursor = self.connection.cursor()

        cursor.execute(f'select * from queue where email="{email}"')
        if list(cursor.fetchall()) == []:
            cursor.execute(
                f'insert into queue (email, stage) values ("{email}", 0)')

        self.connection.commit()
        return {"status": "success"}

    def unsubscribe(self, email):
        cursor = self.connection.cursor()
        cursor.execute(f'delete from queue where email="{email}"')
        self.connection.commit()

        return {"status": "success"}

    def send_nurse_location(self, email, lat, lon):
        cursor = self.connection.cursor()

        cursor.execute(
            f'update nurses set lat={lat}, lon={lon} where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def get_nurse_location(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')

        visit = list(cursor.fetchall())[0]
        nurse_email = visit["nurse_email"]

        if visit["visit_status"] != 0 or visit["on_the_way"] == 0:
            return {"status": "failed"}

        cursor.execute(f'select * from nurses where email="{nurse_email}"')
        nurse = list(cursor.fetchall())[0]
        address = visit["address"]
        api_key = 'AIzaSyAe7nmOwtSLsOdfYwJ_ns3p1krP0h97rPE'
        k = requests.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}")
        location = k.json()["results"][0]["geometry"]["location"]

        dest = str(location["lat"]) + "," + str(location["lng"])

        source = str(nurse["lat"]) + "," + str(nurse["lon"])

        eta = get_duration(source, dest)["data"]

        return {"status": "success", "data": {"lat": nurse["lat"], "lon": nurse["lon"], "eta": eta}}

    def get_tracking_data(self, mrn, patient_email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')
        visit = list(cursor.fetchall())[0]

        if visit["email"] != patient_email:
            return {"status": "failed"}
        nurse_email = visit["nurse_email"]

        cursor.execute(f'select * from nurses where email="{nurse_email}"')
        nurse = list(cursor.fetchall())[0]

        address = visit["address"]
        api_key = 'AIzaSyAe7nmOwtSLsOdfYwJ_ns3p1krP0h97rPE'
        k = requests.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}")
        location = k.json()["results"][0]["geometry"]["location"]

        datetime_str = f'{visit["visit_month"]}/{visit["visit_date"]}/{visit["visit_year"]} '
        datetime_str += parse_time(visit["nurse_time"])
        return {"status": "success", "data": {
            "nurse_name": nurse["name"],
            "nurse_image": nurse["image"],
            "nurse_phone": nurse["phone"],
            "address": visit["address"],
            "datetime_str": datetime_str,
            "lat": location["lat"],
            "lon": location["lng"]
        }}

    def get_patient_visits(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where email="{email}"')
        return {"status": "success", "data": list(cursor.fetchall())}

    def get_logs_data_patient(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from drchrono_request_logs where email="{email}";')
        return {"status": "success", "data": list(cursor.fetchall())}

    def get_healthie_user_data(self, email):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(f'select * from drchrono_request_logs where email="{email}";')
            req_logs = cursor.fetchone()
            logger.info('get_healthie_user_data: row=' + str(req_logs))
            profile = json.loads(req_logs.get('request_params'))
            height = profile.get('healthie_data').get('height')
            weight = profile.get('healthie_data').get('weight')
            dob = profile.get('healthie_data').get('dob')
            address = profile.get('profile_data').get('patient_address')
            form_answers = profile.get('healthie_data').get('charting_notes')

            return {"status": "success", "data": {"height": height, "weight": weight, "dob": dob, "address": address, "form_answers": form_answers}}
        except Exception as e:
            logger.exception("get_healthie_user_data => " + str(e))
            return {"status": "failed", "error": str(e)}

    def get_is_amazon_unprocessed_visits(self):
        """
        Get visits where is_amazon=1, curexa_processed=0 and intake isn't filled in 72 hours
        """
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(f'select * from visits where is_amazon=1 and curexa_processed=0 and Is_user_verified is null;')
            return {"status": "success", "data": list(cursor.fetchall())}
        except Exception as e:
            logger.exception("get_is_amazon_unprocessed_visits => " + str(e))

    def update_curexa_processed(self, mrn):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(f"update visits set curexa_processed=1 where mrn='{mrn}';")
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            logger.exception("update_curexa_processed => " + str(e))

    def get_patient_questions(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from question where mrn="{mrn}"')
        return {"status": "success", "data": list(cursor.fetchall())}

    def get_visits(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where email="{email}"')
        return {"status": "success", "data": list(cursor.fetchall())}

    def get_visits_data_by_mrn(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')
        return {"status": "success", "data": list(cursor.fetchall())}

    def get_visits_data_by_is_healthie(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM nextmed.visits where is_healthie = 1 and insurance_elig_checked is null and is_user_verified = 1')
        return {"status": "success", "data": list(cursor.fetchall())}

    def get_visits_data_for_patient_id_md(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select patient_id_md, current_medications, allergies, patient_test_type from '
            f'nextmed.visits where patient_id_md is not null and length(patient_id_md) > 10 '
            f'and patient_id_md not in ("None", "", "0")'
        )
        return {"status": "success", "data": list(cursor.fetchall())}

    def update_signed_contract(self, url, mrn, signed_date):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f"update visits set Signature='{url}', Signature_time='{signed_date}' where mrn='{mrn}';")
        self.connection.commit()
        return {"status": "success"}

    def update_drchrono_res_req_column(self, url, mrn, column):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"update visits set {column}='{url}' where mrn='{mrn}';")
        self.connection.commit()
        return {"status": "success"}

    def get_patient_subscription(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        if email == "test@yomail.com":
            cursor.execute(f'select * from Subscription')
        else:
            cursor.execute(f'select * from Subscription where email="{email}"')
        return {"status": "success", "data": list(cursor.fetchall())}

    def add_doctor_result(self, mrn, test, results):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        result_id = get_random_str(8)
        cursor.execute(
            f"insert into doctor_results (result_id, mrn, test, results) values ('{result_id}', '{mrn}', '{test}', '{results}');")

        cursor.execute(f'select * from visits where mrn="{mrn}";')

        visit = list(cursor.fetchall())[0]

        email = visit["email"]
        name = visit["patient_name"]
        phone_number = visit["phone"]

        self.send_klaviyo_results_request(
            self, email, name, phone_number, test, mrn)

        self.connection.commit()
        return {"status": "success"}

    def edit_doctor_result(self, result_id, new_results):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            f"update doctor_results set results='{new_results}' where result_id='{result_id}';")
        self.connection.commit()
        return {"status": "success"}

    def delete_doctor_result(self, result_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            f'delete from doctor_results where result_id="{result_id}"')
        self.connection.commit()
        return {"status": "success"}

    def get_doctor_result(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(f'select * from doctor_results where mrn="{mrn}";')
        final = list(cursor.fetchall())

        x = []

        try:
            cursor.execute(f'select * from visits where mrn="{mrn}";')
            note = list(cursor.fetchall())[0]["note_to_patient"]
        except:
            note = "N/A"

        for ii in final:
            ii["note_to_patient"] = note
            x.append(ii)
        return {"status": "success", "data": x}

    def get_possible_times(self, current_date, current_month, current_year, zip_code, current_time, doctor_email,
                           location):
        if zip_code == "":
            return [{"label": "Available Times", "options": []}]

        days = ["monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday"]
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select * from nurses where doctor_email="{doctor_email}" and location="{location}"')
        all_nurses = list(cursor.fetchall())

        day_of_the_week = date(
            current_year, current_month, current_date).weekday()
        intervals = []

        for nurse in all_nurses:

            start_time = nurse[days[day_of_the_week] + "_start"]
            end_time = nurse[days[day_of_the_week] + "_end"]

            if start_time != -1 and end_time != -1:
                if current_time > start_time:
                    start_time = current_time

                if current_time > end_time:
                    end_time = current_time
                cursor.execute(
                    f'select * from visits where visit_date={current_date} and visit_month={current_month} and visit_year={current_year} and nurse_email="{nurse["email"]}";')
                visits = list(cursor.fetchall())
                visits = sorted(visits, key=lambda x: x["nurse_time"])

                final_visits = [[start_time, nurse["address"]]]

                for visit in visits:

                    if int(visit["nurse_time"] / 100) > int(current_time / 100):
                        final_visits.append(
                            [visit["nurse_time"], visit["zip_code"]])

                final_visits.append([end_time, zip_code])

                for j in range(0, len(final_visits) - 1):

                    if j == 0:
                        time_delta = 0
                    else:
                        time_delta = 15
                    travel_time_1 = get_travel_time(
                        final_visits[j][1], zip_code)
                    travel_time_2 = get_travel_time(
                        zip_code, final_visits[j + 1][1])

                    if convert_time(final_visits[j][0], travel_time_2 + travel_time_1 + time_delta) < \
                            final_visits[j + 1][0]:
                        interval = []
                        interval.append(nurse["email"])
                        interval.append(travel_time_1)

                        if j == 0:
                            interval.append(final_visits[j][0])
                        else:
                            interval.append(convert_time(
                                final_visits[j][0], travel_time_1 + time_delta))
                        interval.append(convert_time(
                            final_visits[j + 1][0], -1 * travel_time_2))
                        interval.append(nurse["name"])

                        intervals += splice_intervals(interval,
                                                      current_time, end_time)

        intervals = sorted(intervals, key=lambda x: x[2])

        d = {}
        for i in intervals:

            if int(i[2] / 100) % 2 == 1:
                time_key = int(i[2] / 100) - 1
            else:
                time_key = int(i[2] / 100)
            if time_key in d:
                d[time_key].append(i)
            else:
                d[time_key] = [i]
        options = []
        for i in d:
            f = min(d[i], key=lambda x: x[1])
            l = len(d[i])
            options.append({"label": get_nurse_time_interval(f[2], f[3]), "value": {
                "time": f[2], "email": f[0], "nurse_name": f[4], "num_slots": l}})

        return [{"label": "Available Times", "options": options}]

    # def get_possible_times(self, current_date, current_month, current_year, address, current_time):

    #     day_of_the_week = date(current_year, current_month, current_date).weekday()

    #     if day_of_the_week == 6:
    #         return [{"label":"Available Times", "options":[]}]
    #     cursor = self.connection.cursor(pymysql.cursors.DictCursor)
    #     cursor.execute(f'select * from visits where visit_date={current_date} and visit_month={current_month} and visit_year={current_year} and is_family=0 and refunded=0')

    #     visits = list(cursor.fetchall())
    #     all_times = [800, 1000, 1200, 1400, 1600, 1800]

    #     temp_times = []
    #     for i in all_times:
    #         if i > current_time:
    #             temp_times.append(i)
    #     all_times = temp_times

    #     slot_counts = {}

    #     for i in visits:
    #         rounded_time = int(i["nurse_time"]/100) * 100
    #         if rounded_time in slot_counts:
    #             slot_counts[rounded_time] += 1
    #         else:
    #             slot_counts[rounded_time] = 1

    #     options = []
    #     for i in all_times:
    #         if i in slot_counts:
    #             if slot_counts[i] == 1:
    #                 options.append({"label":f'{parse_time(i)} - {parse_time(i + 200)}', "value":{"time":i + 30, "email":"natasha@joinnextmed.com"}})
    #             elif slot_counts[i] == 2:
    #                 options.append({"label":f'{parse_time(i)} - {parse_time(i + 200)}', "value":{"time":i + 100, "email":"natasha@joinnextmed.com"}})
    #             elif slot_counts[i] == 3:
    #                 options.append({"label":f'{parse_time(i)} - {parse_time(i + 200)}', "value":{"time":i + 130, "email":"natasha@joinnextmed.com"}})
    #         else:
    #             options.append({"label":f'{parse_time(i)} - {parse_time(i + 200)}', "value":{"time":i, "email":"natasha@joinnextmed.com"}})
    #     return [{"label":"Available Times", "options":options}]

    def upload_sftp_results(self, order_id, pdf, test_name):

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(f'select * from visits where order_id="{order_id}"')

        visits = list(cursor.fetchall())

        if len(visits) == 0:
            return
        else:
            visit = visits[0]

            if visit["is_uploaded"] == 1:
                return
            else:
                try:
                    self.send_auto_upload_email(
                        visit["patient_name"], "veer@joinnextmed.com")
                    self.send_auto_upload_email(
                        visit["patient_name"], "frank@joinnextmed.com")
                    self.send_auto_upload_email(
                        visit["patient_name"], "caroline@joinnextmed.com")
                except Exception as e:
                    pass
                print(
                    f'SENDING RESULT for {visit["patient_name"]}, {visit["visit_month"]}/{visit["visit_date"]}/{visit["visit_year"]}')
                self.send_result(visit["email"], visit["visit_date"], visit["visit_month"], visit["visit_year"], [
                    pdf], visit["patient_name"], visit["phone"], visit["mrn"],
                                 [visit["patient_name"].replace(" ", "_") + ".pdf"], test_name)

    def add_patient(self, patient_id, doctor_email, visit_date, visit_month, visit_year, visit_time, patient_name,
                    email,
                    phone, address, notes, dob_date, dob_month, dob_year, sex, insurance, chief_complaint, urine,
                    strep, flu, covid, ecg, viral, spirometry, blood, current_date, current_month, current_year,
                    current_time, doctor_name, nurse_time, nurse_email, apartment_number, house_member, mobile, live,
                    is_family, requested_tests, zip_code, is_flight, location, payment_token, payment_price,
                    card_token):
        if payment_token != "":
            if email == "nand.vinchhi@gmail.com" or email == "veergadodia24@gmail.com" or email == "frank@joinnextmed.com":
                charge = stripe.Charge.create(
                    amount=50,
                    currency='usd',
                    description='Add patient charge',
                    source=payment_token["id"],
                )
            else:
                charge = stripe.Charge.create(
                    amount=payment_price * 100,
                    currency='usd',
                    description='Add patient charge',
                    source=payment_token["id"],
                )
            try:
                if is_prod == True and email != "veergadodia24@gmail.com" and email != "nand.vinchhi@gmail.com":
                    self.send_email_on_booking(location, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), requested_tests, "rob@joinnextmed.com")
                    self.send_email_on_booking(location, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), requested_tests, "hannah@joinnextmed.com")
                    self.send_email_on_booking(location, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), requested_tests, "veer@joinnextmed.com")
                    self.send_email_on_booking(location, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), requested_tests, "svarlotta@joinnextmed.com")
                    self.send_email_on_booking(location, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), requested_tests, "cam463@cornell.edu")
                    self.send_email_on_booking(location, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), requested_tests, "frank@joinnextmed.com")

            except Exception as e:
                pass

        try:

            customer = stripe.Customer.create(
                source=card_token,
                email=email,
            )

        except Exception as e:

            customer = {"id": ""}

        current_date = int(current_date)
        age = calculate_age(date(int(dob_year), int(dob_month), int(dob_date)))
        current_month = int(current_month)
        current_year = int(current_year)
        visit_date = int(visit_date)
        visit_month = int(visit_month)
        visit_year = int(visit_year)
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        mrn = get_random_str(8)

        cursor.execute(f'select * from nurses where email="{nurse_email}"')

        try:
            nn = list(cursor.fetchall())[0]
        except:
            nn = {"name": "N/A", "token": ""}

        if patient_id == "":
            patient_id = self.create_patient(doctor_email, patient_name, email, phone, address,
                                             age, -1, insurance, apartment_number, f'{dob_month}/{dob_date}/{dob_year}')
        else:
            update_patient_query = f'update patients set patient_name="{patient_name}", phone="{phone}", address="{address}", age={age}, sex={sex}, apartment_number="{apartment_number}" where patient_id="{patient_id}"'
            cursor.execute(update_patient_query)

        nurse_name = nn["name"]

        expo_token = nn["token"]

        if current_date == visit_date and current_month == visit_month and current_year == visit_year:
            try:
                response = PushClient().publish(PushMessage(
                    to=expo_token,
                    title=f'Visit at {parse_time(int(nurse_time))}',
                    body=f'You have a new visit today at {parse_time(int(nurse_time))}',
                    data=None))
            except:
                pass

        physical_exam_notes = ""
        visit_status = 0
        height = 0
        weight = 0
        bmi = 0
        blood_pressure = ""
        spo2 = 0
        heart_rate = 0
        respiratory_rate = 0
        temperature = 0
        height_percentile = 0
        weight_percentile = 0
        bmi_percentile = 0
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        c_date = date(current_year, current_month, current_date)
        v_date = date(visit_year, visit_month, visit_date)

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]
        if c_date == v_date:
            date_str = "today"
        elif (v_date - c_date).days <= 1:
            date_str = "tomorrow"
        else:
            date_str = calendar.day_name[v_date.weekday(
            )] + ", " + months[visit_month - 1] + " " + str(visit_date)

        # try:
        #     signup_patient(email, patient_name)
        # except:
        #     print("EMAIL ALREADY EXISTS")

        if sex == "":
            sex = -1

        x = (f'insert into visits (mrn, doctor_email, nurse_email, visit_status, visit_date, visit_month, visit_year, '
             f'visit_time, patient_name, email, phone, address, notes, dob_date, dob_month, dob_year, age, sex, insurance, '
             f'chief_complaint, physical_exam_notes, urine, strep, flu, covid, ecg, viral, spirometry, blood, height, weight, '
             f'bmi, height_percentile, weight_percentile, bmi_percentile, blood_pressure, spo2, heart_rate, respiratory_rate, temperature, nurse_time, apartment_number, doctor_name, mobile, visit_duration, patient_id, live, consumer_notes, race, is_family, customer_id, payment_id, refunded, is_uploaded, zip_code, nurse_name, is_flight, order_id, accession_number, note_to_patient, is_complete_doctor, passport_number, is_approved, is_hiv, on_the_way, is_late, booking_date, booking_month, booking_year, booking_time, is_positive, location, number_of_lines, completed_timestamp) values ('
             f'"{mrn}", "{doctor_email}", "{nurse_email}", {visit_status}, {visit_date}, {visit_month}, {visit_year}, '
             f'{visit_time}, "{patient_name}", "{email}", "{phone}", "{address}", "{notes}", {dob_date}, {dob_month}, '
             f'{dob_year}, {age}, {sex}, "{insurance}", "{chief_complaint}", "{physical_exam_notes}", {urine}, {strep}, '
             f'{flu}, {covid}, {ecg}, {viral}, {spirometry}, {blood}, {height}, {weight}, {bmi}, '
             f'{height_percentile}, {weight_percentile}, {bmi_percentile}, "{blood_pressure}", {spo2}, {heart_rate}, '
             f'{respiratory_rate}, {temperature}, "{nurse_time}", "{apartment_number}", "{doctor_name}", {mobile}, -1, "{patient_id}", {live}, "{requested_tests}", "", {is_family}, "{customer["id"]}", "{payment_token}", 0, 0, "{zip_code}", "{nurse_name}", {is_flight}, -1, -1, "", 0, "", 0, 1, 0, 0, {current_date}, {current_month}, {current_year}, {current_time}, 0, "{location}", 0, "");')

        cursor.execute(x)
        self.connection.commit()

        cursor.execute(f'select * from visits where mrn="{mrn}"')
        row = list(cursor.fetchall())[0]
        try:
            f_date = datetime(year=row['visit_year'], month=row['visit_month'],
                              day=row['visit_date']).strftime("%m/%d/%Y")
        except:
            f_date = "NA"

        patient_sex = "Female" if (row['sex'] == SEX_FEMALE) else "Male"

        x = row
        x["name"] = row["patient_name"]
        x["sex"] = patient_sex

        x["dob"] = f'{row["dob_month"]}/{row["dob_date"]}/{row["dob_year"]}'
        x["receipt_email"] = row["email"]
        x["requested_tests"] = row["consumer_notes"]
        x["exact_nurse_time"] = row["nurse_time"]
        x["parsed_exact_nurse_time"] = parse_time(row["nurse_time"])
        x["flight_timestamp"] = row["flight_time"]
        x["complaint"] = row["chief_complaint"]
        x["date"] = f_date
        x["time"] = str(row['visit_time'])

        if int(row["nurse_time"] / 100) % 2 == 0:
            x["nurse_time"] = parse_time(int((row["nurse_time"]) / 100) * 100) + \
                              " - " + parse_time(int((row["nurse_time"]) / 100) * 100 + 200)
        else:
            x["nurse_time"] = parse_time(int((row["nurse_time"]) / 100) * 100 - 100) + \
                              " - " + parse_time(int((row["nurse_time"]) / 100) * 100 + 100)
        return mrn, x

    def edit_payment_id_with_mrn(self, subId, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        r = cursor.execute(
            f'update visits set payment_id="{subId}" where mrn="{mrn}";'

        )
        return {"status": "success"}

    def change_membership_val(self, mrn):
        val = "Yes"
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        r = cursor.execute(
            f'update visits set is_membership="{val}" where mrn="{mrn}";'

        )
        return {"status": "success"}

    def create_coupon(self, amount, coupon_type, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        coupon_id = "SAVE10"
        cursor.execute(
            f'insert into coupons (id, type, value, email) values ("{coupon_id}", "{coupon_type}", {amount}, "{email}")')

        self.connection.commit()
        return coupon_id

    def add_pa_data(self, patient_name,
                        email,
                        date_purchased,
                        subscription_status,
                        payment_status,
                        next_billing,
                        notes,
                        action_taken,
                        patient_insurance_name,
                        pa_status,
                        mdi_status,
                        insurance_group,
                        ozempic_pa_status,
                        saxenda_pa_status,
                        rybelsus_pa_status,
                        mounjaro_pa_status,
                        reminder_sent,
                        intake_reminder,
                        insurance_id,
                        phone_number,
                        agent,
                        last_modified,
                        created,
                        day_status,
                        status):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'insert into pa_auth (patient_name, email, date_purchased, subscription_status , payment_status, next_billing, notes , action_taken , patient_insurance_name , pa_status, mdi_status , insurance_group , ozempic_pa_status ,saxenda_pa_status,rybelsus_pa_status,   mounjaro_pa_status, reminder_sent,  intake_reminder , insurance_id, phone_number, agent, last_modified, created, seven_day_status, status) values ("{patient_name}", "{email}","{date_purchased}", {subscription_status}, "{payment_status}", "{next_billing}", "{notes}", "{action_taken}", "{patient_insurance_name}", "{pa_status}", "{mdi_status}", "{insurance_group}", "{ozempic_pa_status}", "{saxenda_pa_status}", "{rybelsus_pa_status}", "{mounjaro_pa_status}", "{reminder_sent}", "{intake_reminder}", "{insurance_id}", "{phone_number}", "{agent}", "{last_modified}", "{created}", "{day_status}", "{status}")')

        self.connection.commit()
        return {"status": "success"}

    def apply_coupon(self, coupon_id, email):

        if coupon_id == "SAVE10" or coupon_id == "MOM21" or coupon_id == "FB10":
            return {"status": "success", "data": {"id": coupon_id, "type": "percentage", "value": 10, "email": ""}}
        elif coupon_id == "FRIENDSFAMILY2021":
            return {"status": "success", "data": {"id": coupon_id, "type": "percentage", "value": 100, "email": ""}}

        else:
            return {"status": "failed"}
        # cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        # cursor.execute(f'select * from coupons where id="{coupon_id}"')
        # coupons = list(cursor.fetchall())
        # if coupons == []:
        #     return {"status": "failed"}
        # else:
        #     coupon = coupons[0]
        #     if coupon["email"] == email:
        #         cursor.execute(f'delete from coupons where id="{coupon_id}"')
        #         self.connection.commit()
        #         return {"status": "success", "data": coupons[0]}
        #     else:
        #         return {"status": "failed"}

    def consumer_add_patient(self, visit_date, visit_month, visit_year, patient_name, phone, address, current_date,
                             current_month, current_year, current_time, nurse_time, nurse_email, apartment_number,
                             consumer_notes,
                             receipt_email, dob_month, dob_date, dob_year, sex, race, options, is_family, flight_time,
                             card_token,
                             payment_id, zip_code, is_flight, is_hiv, doctor_email, location, patient_symptoms,
                             axle_patient, axle_address,
                             provider, is_insurance, lab_fax, price, test_type, insuranceAmt, insurance, region_no,
                             customer_id, patient_id_md, patient_id, path, subscription_id, subscription, coupon,
                             total_price, height, weight,airtable_id,consent,order_test_id,total_discount,referrer = None,agent_name="Next-Medical"):
        # print(provider)
        birthDate = date(dob_year, dob_month, dob_date)
        age = calculate_age(birthDate)
        current_date = int(current_date)
        current_month = int(current_month)
        current_year = int(current_year)
        visit_date = int(visit_date)
        visit_month = int(visit_month)
        visit_year = int(visit_year)
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        email = receipt_email
        mrn = get_random_str(8)
        region_no = region_no

        nn = {"name": "N/A", "token": ""}
        nurse_name = nn["name"]

        # try:
        #     customer = stripe.Customer.create(
        #         source=card_token,
        #         email=email,

        #     )

        # except Exception as e:

        # customer = {"id":""}

        visit_time = 0

        notes = ""

        try:
            if address.split()[0].lower() == "home":
                insurance = "Yes"
                if phone != "":
                    self.send_patient_message(
                        patient_name, "", phone, "checkout_with_home")
            else:
                if is_insurance == 1:
                    insurance = "Yes"
                    if phone != "":
                        self.send_patient_message(
                            patient_name, "", phone, "checkout_with_insurance")
                else:
                    insurance = "No"
                    if phone != "":
                        self.send_patient_message(
                            patient_name, "", phone, "checkout_without_insurance")
        except Exception as e:
            logger.exception(e)

        chief_complaint = options
        urine = 0
        strep = 0
        flu = 0
        covid = 0
        ecg = 0
        viral = 0
        spirometry = 0
        blood = 0
        doctor_name = ""
        house_member = 0
        mobile = 0
        live = 0
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        # print("date and time =", dt_string)

        if sex == 0:
            final_sex = "M"
        elif sex == 1:
            final_sex = "F"
        elif sex == 2:
            final_sex = ""
        else:
            final_sex = "O"

        try:
            cursor.execute(f'select * from visits where email="{email}"')

            data = list(cursor.fetchall())

            for i in range(0, len(data)):
                data[i]["sortable_date"] = int(data[i]["booking_year"]) * 100000000 + int(
                    data[i]["booking_month"]) * 1000000 + int(data[i]["booking_date"]) * 10000 + int(
                    data[i]["booking_time"])

            final = max(data, key=lambda x: x["sortable_date"])

            # if insurance == "Yes":
            #     if final["insurance"] != "Yes" or final["insurance"] != "No":
            #         insurance = final["insurance"]

            dob_date = final["dob_date"]
            dob_month = final["dob_month"]
            dob_year = final["dob_year"]
            birthDate = date(dob_year, dob_month, dob_date)
            age = calculate_age(birthDate)

            sex = final["sex"]
            if sex == 0:
                final_sex = "M"
            elif sex == 1:
                final_sex = "F"
            elif sex == 2:
                final_sex = ""
            else:
                final_sex = "O"

            pharmacy = final["pharmacy"]
            patient_address = ""

        except Exception as e:
            logger.exception(e)
            pharmacy = ""
            patient_address = ""

        '''try:

            if provider == "labcorp":
                print(generate_labcorp_pdf(options, is_insurance, patient_name, dob_month, dob_date,
                      dob_year, receipt_email, phone[-10::], final_sex, lab_fax, mrn, insurance, region_no))
            elif provider == "empire":
                print(generate_empire_pdf(options, is_insurance, patient_name, dob_month, dob_date,
                      dob_year, receipt_email, phone[-10::], final_sex, lab_fax, mrn, insurance))
            elif provider == "northwell":
                print(generate_northwell_pdf(options, is_insurance, patient_name, dob_month, dob_date,
                      dob_year, receipt_email, phone[-10::], final_sex, lab_fax, mrn, insurance))
            else:
                print(generate_quest_pdf(options, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
                    dob_year), receipt_email, phone[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))

        except Exception as e:
            logger.exception(e)
            # print("Fax failed with error: ", str(e))'''

        try:
            if is_prod is True and email != "veergadodia24@gmail.com" and email != "nand.vinchhi@gmail.com" and email != "smart1@gmail.com":
                if test_type != "std" or test_type != "hiv" or test_type != "herpes":
                    # self.send_email_on_booking_new(address, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                    #     nurse_time), options, "rob@joinnextmed.com", path, total_price, "Rob")
                    self.send_email_on_booking_new(address, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), options, "frank@joinnextmed.com", path, total_price, "Frank")

        except Exception as e:
            logger.exception(e)

        # add entry to googlesheet
        if is_prod is True:
            append_to_gsheet(path, total_price)

        # print("twoo")
        expo_token = nn["token"]

        """
        if current_date == visit_date and current_month == visit_month and current_year == visit_year:
            try:
                response = PushClient().publish(PushMessage(
                    to=expo_token,
                    title=f'Visit at {parse_time(int(nurse_time))}',
                    body=f'You have a new visit today at {parse_time(int(nurse_time))}',
                    data=None))
            except Exception as e:
                logger.exception(e)
        """

        physical_exam_notes = ""
        visit_status = 0
        height = 0
        weight = 0
        bmi = 0
        blood_pressure = ""
        spo2 = 0
        heart_rate = 0
        respiratory_rate = 0
        temperature = 0
        height_percentile = 0
        weight_percentile = 0
        bmi_percentile = 0
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # try:
        #     self.send_patient_email(email, patient_name.split(" ")[0], "NA", "NA", address)
        # except Exception as e:
        #     pass

        try:
            self.send_klaviyo_track_request(
                email, patient_name, phone, options, price, is_insurance, test_type, address, insuranceAmt, mrn)
        except Exception as e:
            logger.error("Error with klaviyo")
            logger.exception(e)

        try:
            self.send_klaviyo_post_track_request(email, patient_name, price)
        except Exception as e:
            logger.error("Error with klaviyo")
            logger.exception(e)

        # try:
        #     signup_patient(email, patient_name)
        # except:
        #     print("EMAIL ALREADY EXISTS")

        x = (f'insert into visits (mrn, doctor_email, nurse_email, visit_status, visit_date, visit_month, visit_year, '
             f'visit_time, patient_name, email, phone, address, notes, dob_date, dob_month, dob_year, age, sex, insurance, '
             f'chief_complaint, physical_exam_notes, urine, strep, flu, covid, ecg, viral, spirometry, blood, height, weight, '
             f'bmi, height_percentile, weight_percentile, bmi_percentile, blood_pressure, spo2, heart_rate, respiratory_rate, temperature, '
             f'nurse_time, apartment_number, doctor_name, mobile, visit_duration, patient_id,patient_id_md, live, consumer_notes, race, is_family, flight_time, '
             f'customer_id, payment_id, refunded, is_uploaded, zip_code, nurse_name, is_flight, order_id, accession_number, note_to_patient, '
             f'is_complete_doctor, passport_number, is_approved, is_hiv, on_the_way, is_late, booking_date, booking_month, booking_year, booking_time, is_positive, location, number_of_lines, completed_timestamp, patient_symptoms, axle_patient, axle_address, pharmacy, patient_address, lab_fax, server_date_time,subscription_id,coupon,price,airtable_id,total_price,consent_klaviyo,order_test_id,total_discount,referrer,agent_name) values ('
             f'"{mrn}", "{doctor_email}", "{nurse_email}", "{visit_status}", "{visit_date}", "{visit_month}", "{visit_year}", '
             f'"{visit_time}", "{patient_name}", "{email}", "{phone}", "{address}", "{notes}", "{dob_date}", "{dob_month}", '
             f'"{dob_year}", "{age}", "{0}", "{insurance}", "{chief_complaint}", "{physical_exam_notes}", "{urine}", "{strep}", '
             f'"{flu}", "{covid}", "{ecg}", "{viral}", "{spirometry}", "{blood}", "{height}", "{weight}", "{bmi}", '
             f'"{height_percentile}", "{weight_percentile}", "{bmi_percentile}", "{blood_pressure}", "{spo2}", "{heart_rate}", '
             f'"{respiratory_rate}", "{temperature}", "{nurse_time}", "{apartment_number}", "{doctor_name}", {mobile}, -1, "{patient_id}", "{patient_id_md}", '
             f'{live}, "{options}", "{race}", {is_family}, "{flight_time}", "{customer_id}", "{payment_id}", 0, 0, "{zip_code}", "{nurse_name}", {is_flight}, -1, -1, "", 0, "", 0, {is_hiv}, 0, 0, {current_date}, {current_month}, {current_year}, {current_time}, 0, "{location}", 0, "", "{patient_symptoms}", "{axle_patient}", "{axle_address}", "{pharmacy}", "{patient_address}", "{lab_fax}" ,"{dt_string}","{subscription_id}","{coupon}","{price}","{airtable_id}","{total_price}","{consent}","{order_test_id}","{total_discount}","{referrer}","{agent_name}");')

        cursor.execute(x)
        self.connection.commit()

        logger.info(
            f'Patient Booked! Name is {patient_name}, email is {email} and phone is {phone}.')
        return mrn

    def add_subscription_patient(self, subscription_id, email, testName):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        data = cursor.execute(
            f'insert into Subscription (subscription_id, email, test_name) values("{subscription_id}","{email}","{testName}")')
        self.connection.commit()
        return data

    def add_subscription_patient_prescriptions(self, subscription_id, email, testName):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        type = "prescription"
        data = cursor.execute(
            f'insert into Subscription (subscription_id, email, test_name , type) values("{subscription_id}","{email}","{testName}","{type}")')
        self.connection.commit()
        return data

    def consumer_add_patient_test(self, visit_date, visit_month, visit_year, patient_name, phone, address, current_date,
                                  current_month, current_year, current_time, nurse_time, nurse_email, apartment_number,
                                  consumer_notes,
                                  receipt_email, dob_month, dob_date, dob_year, sex, race, options, is_family,
                                  flight_time, card_token,
                                  payment_id, zip_code, is_flight, is_hiv, doctor_email, location, patient_symptoms,
                                  axle_patient, axle_address,
                                  provider, is_insurance, lab_fax, price, insuranceAmt, insurance, region_no,
                                  customer_id, patient_id_md, patient_id):
        print(provider)
        birthDate = date(dob_year, dob_month, dob_date)
        age = calculate_age(birthDate)
        current_date = int(current_date)
        current_month = int(current_month)
        current_year = int(current_year)
        visit_date = int(visit_date)
        visit_month = int(visit_month)
        visit_year = int(visit_year)
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        email = receipt_email
        region_no = region_no

        nn = {"name": "N/A", "token": ""}
        nurse_name = nn["name"]

        # try:
        #     customer = stripe.Customer.create(
        #         source=card_token,
        #         email=email,

        #     )

        # except Exception as e:

        # customer = {"id":""}

        visit_time = ""

        notes = ""

        if is_insurance == 1:
            insurance = "Yes"
        else:
            insurance = "No"

        urine = 0
        strep = 0
        flu = 0
        covid = 0
        ecg = 0
        viral = 0
        spirometry = 0
        blood = 0
        doctor_name = ""
        house_member = 0
        mobile = 0
        live = 0
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print("date and time =", dt_string)

        if sex == 0:
            final_sex = "M"
        elif sex == 1:
            final_sex = "F"
        elif sex == 2:
            final_sex = ""
        else:
            final_sex = "O"

        try:
            cursor.execute(f'select * from visits where email="{email}"')

            data = list(cursor.fetchall())

            for i in range(0, len(data)):
                data[i]["sortable_date"] = int(data[i]["booking_year"]) * 100000000 + int(
                    data[i]["booking_month"]) * 1000000 + int(data[i]["booking_date"]) * 10000 + int(
                    data[i]["booking_time"])

            final = max(data, key=lambda x: x["sortable_date"])

            if insurance == "Yes":
                if final["insurance"] != "Yes" or final["insurance"] != "No":
                    insurance = final["insurance"]

            dob_date = final["dob_date"]
            dob_month = final["dob_month"]
            dob_year = final["dob_year"]
            birthDate = date(dob_year, dob_month, dob_date)
            age = calculate_age(birthDate)

            sex = final["sex"]
            if sex == 0:
                final_sex = "M"
            elif sex == 1:
                final_sex = "F"
            elif sex == 2:
                final_sex = ""
            else:
                final_sex = "O"

            pharmacy = final["pharmacy"]
            patient_address = final["patient_address"]
        except:
            pharmacy = ""
            patient_address = ""
        mrn_details = ""
        for test in options:
            mrn = get_random_str(8)
            mrn_details = mrn + mrn_details
            print(mrn_details)
            print(test["test_name"])
            print(test["test_type"])
            try:

                if provider == "labcorp":
                    print(generate_labcorp_pdf(test["test_name"], is_insurance, patient_name, dob_month, dob_date,
                                               dob_year, receipt_email, phone[-10::], final_sex, lab_fax, mrn,
                                               insurance, region_no))
                elif provider == "empire":
                    print(generate_empire_pdf(test["test_name"], is_insurance, patient_name, dob_month,
                                              dob_date, dob_year, receipt_email, phone[-10::], final_sex, lab_fax, mrn,
                                              insurance))
                elif provider == "northwell":
                    print(generate_northwell_pdf(test["test_name"], is_insurance, patient_name, dob_month,
                                                 dob_date, dob_year, receipt_email, phone[-10::], final_sex, lab_fax,
                                                 mrn, insurance))
                else:
                    print(generate_quest_pdf(test["test_name"], int(is_insurance), patient_name, int(dob_month), int(
                        dob_date), int(dob_year), receipt_email, phone[-10::], final_sex, str(lab_fax), mrn, insurance,
                                             region_no))

            except Exception as e:

                print("Fax failed with error: ", str(e))

            try:
                if is_prod == True and email != "veergadodia24@gmail.com" and email != "nand.vinchhi@gmail.com" and email != "smart1@gmail.com":
                    self.send_email_on_booking(address, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), test["test_name"], "rob@joinnextmed.com")
                    self.send_email_on_booking(address, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), test["test_name"], "veer@joinnextmed.com")
                    self.send_email_on_booking(address, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                        nurse_time), test["test_name"], "frank@joinnextmed.com")

            except Exception as e:

                pass

            # print("twoo")
            expo_token = nn["token"]

            if current_date == visit_date and current_month == visit_month and current_year == visit_year:
                try:
                    response = PushClient().publish(PushMessage(
                        to=expo_token,
                        title=f'Visit at {parse_time(int(nurse_time))}',
                        body=f'You have a new visit today at {parse_time(int(nurse_time))}',
                        data=None))
                except:
                    pass

            physical_exam_notes = ""
            visit_status = 0
            height = 0
            weight = 0
            bmi = 0
            blood_pressure = ""
            spo2 = 0
            heart_rate = 0
            respiratory_rate = 0
            temperature = 0
            height_percentile = 0
            weight_percentile = 0
            bmi_percentile = 0
            twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            if phone != "":
                sms = "Hi " + patient_name.split(" ")[
                    0] + ", your Next Medical visit has been scheduled at the     location: " + \
                      address + ". Please bring your insurance card if you opted to use it for lab processing."

                sms += "\n\nFor more information on how the visit works, visit our website at https://www.joinnextmed.  com"

                try:
                    message = send_text_message(str(phone), sms)
                    # message = twilio_client.messages.create(
                    #     body=sms,
                    #     from_='+18454069635',
                    #     to='+1' + str(phone))

                except Exception as e:
                    pass

            # try:
            #     self.send_patient_email(email, patient_name.split(" ")[0], "NA", "NA", address)
            # except Exception as e:
            #     pass

            try:
                self.send_klaviyo_track_request(
                    email, patient_name, phone, test["test_name"], price, is_insurance, test["test_type"], address,
                    insuranceAmt, mrn)
            except Exception as e:
                print("Error with klaviyo")
                pass

            # try:
            #     signup_patient(email, patient_name)
            # except:
            #     print("EMAIL ALREADY EXISTS")

            x = (
                f'insert into visits (mrn, doctor_email, nurse_email, visit_status, visit_date, visit_month,   visit_year, '
                f'visit_time, patient_name, email, phone, address, notes, dob_date, dob_month, dob_year, age, sex,  insurance, '
                f'chief_complaint, physical_exam_notes, urine, strep, flu, covid, ecg, viral, spirometry, blood,    height, weight, '
                f'bmi, height_percentile, weight_percentile, bmi_percentile, blood_pressure, spo2, heart_rate,  respiratory_rate, temperature, '
                f'nurse_time, apartment_number, doctor_name, mobile, visit_duration, patient_id,patient_id_md, live,    consumer_notes, race, is_family, flight_time, '
                f'customer_id, payment_id, refunded, is_uploaded, zip_code, nurse_name, is_flight, order_id,    accession_number, note_to_patient, '
                f'is_complete_doctor, passport_number, is_approved, is_hiv, on_the_way, is_late, booking_date,  booking_month, booking_year, booking_time, is_positive, location, number_of_lines, completed_timestamp,  patient_symptoms, axle_patient, axle_address, pharmacy, patient_address, lab_fax, server_date_time)  values ('
                f'"{mrn}", "{doctor_email}", "{nurse_email}", "{visit_status}", "{visit_date}", "{visit_month}", "  {visit_year}", '
                f'"{visit_time}", "{patient_name}", "{email}", "{phone}", "{address}", "{notes}", "{dob_date}", "   {dob_month}", '
                f'"{dob_year}", "{age}", "{0}", "{insurance}", "{test["test_name"]}", "{physical_exam_notes}", "{urine}",     "{strep}", '
                f'"{flu}", "{covid}", "{ecg}", "{viral}", "{spirometry}", "{blood}", "{height}", "{weight}", "{bmi}", '
                f'"{height_percentile}", "{weight_percentile}", "{bmi_percentile}", "{blood_pressure}", "{spo2}", " {heart_rate}", '
                f'"{respiratory_rate}", "{temperature}", "{nurse_time}", "{apartment_number}", "{doctor_name}", {mobile}    , -1, "{patient_id}", "{patient_id_md}", '
                f'{live}, "{test["test_name"]}", "{race}", {is_family}, "{flight_time}", "{customer_id}", "{payment_id}", 0, 0, " {zip_code}", "{nurse_name}", {is_flight}, -1, -1, "", 0, "", 0, {is_hiv}, 0, 0, {current_date},  {current_month}, {current_year}, {current_time}, 0, "{location}", 0, "", "{patient_symptoms}", " {axle_patient}", "{axle_address}", "{pharmacy}", "{patient_address}", "{lab_fax}" ,"{dt_string}");')

            cursor.execute(x)
            self.connection.commit()
            print(
                f'Patient Booked! Name is {patient_name}, email is {email} and phone is {phone}.')

        if phone != "":
            self.send_patient_message(patient_name, "", phone, "checkout")
        return mrn_details

    def update_pharmacy_and_insurance(self, insurance, pharmacy, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set insurance="{insurance}", pharmacy="{pharmacy}" where mrn="{mrn}";')
        self.connection.commit()

        return {"status": "success"}

    def set_positive(self, mrn, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set is_positive={value} where mrn="{mrn}"')
        self.connection.commit()
        return {"status": "success"}

    def set_on_the_way(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')
        visit = list(cursor.fetchall())[0]
        phone = visit["phone"]
        cursor.execute(f'update visits set on_the_way=1 where mrn="{mrn}"')
        self.connection.commit()
        try:
            sms = f'Hi {visit["patient_name"].split(" ")[0]}, your Next Medical Medical Assistant is on the way to your home. track your visit live at https://joinnextmed.com/track?mrn={mrn}'
            message = send_text_message(str(phone), sms)
            # message = twilio_client.messages.create(
            #     body=sms,
            #     from_='+18454069635',
            #     to='+1' + str(phone))
        except:
            pass
        try:
            self.send_on_the_way_email(
                visit["email"], visit["patient_name"], mrn)
        except:
            pass

        cursor.execute(
            f'select * from visits where nurse_email="{visit["nurse_email"]}" and visit_date={visit["visit_date"]} and visit_month={visit["visit_month"]} and visit_year={visit["visit_year"]} and is_late=0 and nurse_time > {visit["nurse_time"]}')

        future_visits = list(cursor.fetchall())
        expected_time = visit["nurse_time"]
        starting_address = visit["address"]

        time_delta = 15
        for i in future_visits:
            expected_time = convert_time(
                expected_time, time_delta + get_travel_time1(starting_address, i["address"]))
            starting_address = i["address"]

            if expected_time <= get_upper_bound(i["nurse_time"]):
                break
            else:
                cursor.execute(
                    f'update visits set is_late=1 where mrn="{i["mrn"]}"')
                try:
                    sms = f'Hi {visit["patient_name"].split(" ")[0]}, we are very sorry to inform you that your Next Medical Medical Assistant is delayed due to high traffic congestion.'
                    message = send_text_message(str(phone), sms)
                    # message = twilio_client.messages.create(
                    #     body=sms,
                    #     from_='+18454069635',
                    #     to='+1' + str(i["phone"]))
                except:
                    pass

        return {"status": "success"}

    def get_autofill_data(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where email="{email}"')
        visits = list(cursor.fetchall())
        visit = visits[-1]

        if visit["sex"] == 0:
            patient_sex = "Male"
        elif visit["sex"] == 1:
            patient_sex = "Female"
        else:
            patient_sex = "Other"
        final = {
            "name": visit["patient_name"],
            "phone": visit["phone"],
            "dob_date": visit["dob_date"],
            "dob_month": visit["dob_month"],
            "dob_year": visit["dob_year"],
            "apartment_number": visit["apartment_number"],
            "sex": patient_sex,
            "address": visit["address"]
        }
        return final

    def charge_card(self, customer_id, price):
        charge = stripe.Charge.create(
            amount=price * 100,
            currency='usd',
            customer=customer_id,
        )
        return {"status": "success", "id": charge["id"]}

    def refund(self, mrn, amount):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')
        visit = cursor.fetchall()[0]

        if amount == -1:
            refund = stripe.Refund.create(
                payment_intent=visit["payment_id"],
            )
        else:
            refund = stripe.Refund.create(
                amount=amount * 100,
                payment_intent=visit["payment_id"],
            )
        self.send_refunded_email(visit["email"], visit["patient_name"],
                                 f'{visit["visit_month"]}/{visit["visit_date"]}/{visit["visit_year"]}')
        return {"status": "success", "id": refund["id"]}

    def cancel_visit(self, mrn, is_canceled):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set payment_id="", refunded={is_canceled} where mrn="{mrn}"')
        self.connection.commit()

        return {"status": "success"}

    def verify_dob(self, email, dob_date, dob_month, dob_year):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where email="{email}"')
        visits = list(cursor.fetchall())
        for visit in visits:
            if visit["dob_date"] == dob_date and visit["dob_month"] == dob_month and visit["dob_year"] == dob_year:
                return {"status": "success"}
        return {"status": "failed"}

    def upload_rapid(self, mrn, doctor_result, test_type):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        if test_type == "rapid":
            test_title = "COVID-19 RAPID ANTIGEN"
            test_name = "SARS-CoV-2(COVID-19) by RAPID ANTIGEN"
        elif test_type == "strep":
            test_title = "RAPID STREP"
            test_name = "RAPID STREP TEST"
        elif test_type == "pcr":
            test_title = "COVID-19 PCR"
            test_name = "SARS-COV-2"
        else:
            test_title = "RAPID FLU"
            test_name = "RAPID FLU TEST"

        cursor.execute(f'select * from visits where mrn="{mrn}"')
        visit = list(cursor.fetchall())[0]
        name = visit["patient_name"]
        phone = visit["phone"]
        dob = f'{visit["dob_month"]}/{visit["dob_date"]}/{visit["dob_year"]}'

        age = visit["age"]

        visit_date = f'{visit["visit_month"]}/{visit["visit_date"]}/{visit["visit_year"]}'
        visit_time = parse_time(visit["nurse_time"])

        pdf_file = BytesIO()
        canvas = Canvas(pdf_file, pagesize=A4)
        canvas.setFont("Courier", 9)

        canvas.drawImage("nextmed.png", 1 * cm, 26.9 * cm, 5 * cm, 2 * cm)

        canvas.setFont("Courier-Bold", 14)
        canvas.drawString(8 * cm, 25.4 * cm, "LABORATORY RESULTS")

        canvas.setFont("Courier-Bold", 12)
        canvas.drawString(2 * cm, 24.4 * cm, "PATIENT")

        canvas.setFont("Courier", 10)
        canvas.drawString(2 * cm, 23.4 * cm, f'Name: {name}')
        canvas.drawString(10 * cm, 23.4 * cm, f'Phone: {phone}')
        canvas.drawString(2 * cm, 22.9 * cm, f'DOB: {dob}')
        canvas.drawString(10 * cm, 22.9 * cm, f'Age: {age}')

        if visit["passport_number"] != "":
            canvas.drawString(2 * cm, 22.4 * cm,
                              f'Passport Number: {visit["passport_number"]}')

        canvas.setFont("Courier-Bold", 12)
        canvas.drawString(2 * cm, 21.4 * cm, "SPECIMEN")

        canvas.setFont("Courier", 10)
        canvas.drawString(2 * cm, 20.4 * cm, f'Collection Time: {visit_time}')
        canvas.drawString(10 * cm, 20.4 * cm,
                          f'Order Number: {get_random_str(11).upper()}')
        canvas.drawString(2 * cm, 19.9 * cm, f'Collection Date: {visit_date}')
        canvas.drawString(10 * cm, 19.9 * cm, f'Report Status: FINAL')
        canvas.drawString(2 * cm, 19.4 * cm, f'Received Date: {visit_date}')
        canvas.drawString(10 * cm, 19.4 * cm, f'Report Date: {visit_date}')

        canvas.setFont("Courier-Bold", 12)
        canvas.drawString(2 * cm, 18.4 * cm, "PROVIDER")

        canvas.setFont("Courier", 10)
        canvas.drawString(2 * cm, 17.4 * cm,
                          f'Requesting Provider: Marc Jonathan Serota MD')
        canvas.drawString(
            2 * cm, 16.9 * cm, f'Address: 9071 E. Mississippi Ave. Unit 6C Denver CO 80247')
        canvas.drawString(2 * cm, 16.4 * cm, f'NPI: 1740410463')

        canvas.setFont("Courier-Bold", 12)
        canvas.drawString(2 * cm, 15.4 * cm, test_title)

        canvas.setFont("Courier-Bold", 8)
        canvas.drawString(2 * cm, 14.4 * cm, test_title)
        canvas.drawString(10 * cm, 14.4 * cm, f'Result')

        canvas.setFont("Courier", 9)
        canvas.drawString(2 * cm, 13.9 * cm, test_name)

        if doctor_result == "Positive":
            canvas.setFillColor(red)

        canvas.drawString(10 * cm, 13.9 * cm, doctor_result)
        canvas.setFillColor(black)

        # canvas.setFont("Courier-Bold", 12)
        # canvas.drawString(2 * cm, 12.4 * cm, "PERFORMING LABORATORIES")
        # canvas.setFont("Courier-Bold", 8)
        # canvas.drawString(2 * cm, 11.4 * cm, f'Performing physician:')
        # canvas.drawString(7.5 * cm, 11.4 * cm, f'NPI:')
        # canvas.drawString(10 * cm, 11.4 * cm, f'Group:')

        # canvas.setFont("Courier", 9)

        # canvas.drawString(2 * cm, 10.9 * cm, f'N/A')
        # canvas.drawString(7.5 * cm, 10.9 * cm, f'N/A')
        # canvas.drawString(10 * cm, 10.9 * cm, f'N/A')

        canvas.save()
        pdf_base64 = "data:application/pdf;base64," + \
                     base64.b64encode(pdf_file.getvalue()).decode()
        self.send_result(visit["email"], visit["visit_date"], visit["visit_month"], visit["visit_year"], [
            pdf_base64], visit["patient_name"], visit["phone"], mrn, [f'{name.replace(" ", "_")}.pdf'], test_title,
                         doctor_result)

        return pdf_base64

    def send_result(self, patient_email, visit_date, visit_month, visit_year, pdfs, name, phone, mrn, file_names,
                    test_name, doctor_result="N/A"):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn="{mrn}"')
        res = list(cursor.fetchall())
        print(res)
        for data in res:
            d_name = ""
            # is_valid = self.is_valid_uuid(data['patient_id_md'])
            # print(is_valid)
            if data['patient_id_md'] == None or data['patient_id_md'] == NULL or data['patient_id_md'] == "None":

                name = data['patient_name']
                print("is_not_id")
                print(name)
                SUBJECT = f'Next Medical New Message'
                RECIPIENT = data['email']
                BODY_TEXT = get_mdintegration_case_results_upload(name, "", "")
                msg = MIMEMultipart('alternative')
                msg['Subject'] = SUBJECT
                msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
                msg['To'] = RECIPIENT
                part1 = MIMEText(BODY_TEXT, 'html')
                msg.attach(part1)
                self.send_patient_message(name, "", data["phone"], "result")
                try:
                    server = smtplib.SMTP(HOST, PORT)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(USERNAME_SMTP, PASSWORD_SMTP)
                    server.sendmail(SENDER, RECIPIENT, msg.as_string())
                    server.close()
                except Exception as e:
                    pass
            else:
                print("is_id")
                case_assignment = mdintegrations.mdintegrations_api.get_patient_cases(
                    data['patient_id_md']
                )
                print(case_assignment)
                if case_assignment and case_assignment['data']:
                    for x in case_assignment['data']:
                        if x["case_assignment"] != None:
                            drname = x["case_assignment"]["clinician"]["full_name"]
                            d_name = x["case_assignment"]["clinician"]["full_name"]
                            photourl = "https://www.joinnextmed.com/doctor.jpg"
                            if x["case_assignment"]["clinician"]["photo"] != None:
                                photourl = x["case_assignment"]["clinician"]["photo"]["url"]
                            name = data['patient_name']
                            SUBJECT = f'Next Medical New Message'
                            RECIPIENT = data['email']
                            BODY_TEXT = get_mdintegration_case_results_upload(
                                name, drname, photourl)
                            msg = MIMEMultipart('alternative')
                            msg['Subject'] = SUBJECT
                            msg['From'] = email.utils.formataddr(
                                (SENDERNAME, SENDER))
                            msg['To'] = RECIPIENT
                            part1 = MIMEText(BODY_TEXT, 'html')
                            msg.attach(part1)

                            try:
                                server = smtplib.SMTP(HOST, PORT)
                                server.ehlo()
                                server.starttls()
                                server.ehlo()
                                server.login(USERNAME_SMTP, PASSWORD_SMTP)
                                server.sendmail(
                                    SENDER, RECIPIENT, msg.as_string())
                                server.close()
                            except Exception as e:
                                pass
                self.send_patient_message(
                    data['patient_name'], d_name, data["phone"], "result")
        for i in range(0, len(file_names)):
            result_id = get_random_str(8)
            cursor.execute(
                f'insert into results (result_id, email, visit_date, visit_month, visit_year, pdf, mrn, file_name, result, test_name) values ("{result_id}", "{patient_email}", {visit_date}, {visit_month}, {visit_year}, "{pdfs[i]}", "{mrn}", "{file_names[i]}", "{doctor_result}", "{test_name}");')
        cursor.execute(f'update visits set is_uploaded=1 where mrn="{mrn}"')
        self.connection.commit()

    def get_results_for_mrn(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from results where mrn = "{mrn}"')
        res = list(cursor.fetchall())
        final = []
        for i in res:
            i["date"] = f'{i["visit_month"]}/{i["visit_date"]}/{i["visit_year"]}'
            i["pdf"] = "https://zf7ivuv18l.execute-api.us-east-2.amazonaws.com/dev/get-pdf-result?result_id=" + i[
                "result_id"]
            final.append(i)
        return final

    def get_result_pdf(self, result_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select * from results where result_id = "{result_id}"')
        res = list(cursor.fetchall())[0]
        base64_data = res["pdf"][28:]

        final = base64.b64decode(base64_data)
        return [final, result_id + ".pdf"]

    def get_fax_form(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from fax_forms where mrn = "{mrn}"')
        res = list(cursor.fetchall())[0]
        base64_data = res["pdf"]
        final = base64.b64decode(base64_data)
        return [final, mrn + ".pdf"]

    def send_result_doctor(self, result_id, result):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update results set result="{result}" where result_id="{result_id}"')

        self.connection.commit()

    def healthie_create_endpoint(self, eligibility_check,copay_amount,coinsurance_amount ,email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set eligibility_check="{eligibility_check}",copay_amount="{copay_amount}",coinsurance_amount="{coinsurance_amount}" where email="{email}";'

        )
        self.connection.commit()
        return {"status": "success"}    


    def mark_doctor_complete(self, mrn, is_complete, notes):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set is_complete_doctor={is_complete}, note_to_patient="{notes}" where mrn="{mrn}"')
        self.connection.commit()

    def approve_visit(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'update visits set is_approved=1 where mrn="{mrn}"')
        self.connection.commit()

    def update_healthie(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'update visits set is_healthie=1,is_user_verified=1 where email="{email}"')
        self.connection.commit()

    def update_isVerified(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'update visits set is_user_verified=1 where email="{email}"')
        self.connection.commit()

    def delete_result(self, result_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from results where result_id="{result_id}"')
        result = list(cursor.fetchall())[0]

        cursor.execute(f'delete from results where result_id="{result_id}"')

        cursor.execute(f'select * from results where mrn="{result["mrn"]}"')
        if list(cursor.fetchall()) == []:
            cursor.execute(
                f'update visits set is_uploaded=0 where mrn="{result["mrn"]}"')
        self.connection.commit()

    def get_results(self, email, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select * from results where email = "{email}" and mrn="{mrn}"')
        res = list(cursor.fetchall())[0]
        base64_data = res["pdf"]
        splitval = base64_data.split("data:application/pdf;base64,")[1]
        final = base64.b64decode(splitval)
        return [final, ".pdf"]

    def upload_log(self, mrn, notes, time, log_result):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'insert into patient_logs (mrn, notes, time, log_result) values ("{mrn}", "{notes}", "{time}", "{log_result}")')
        self.connection.commit()

    def create_patient(self, doctor_email, patient_name, email, phone, address, age, sex, insurance, apartment_number,
                       dob):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            f'select * from patients where email="{email}" and patient_name like "{patient_name}";')

        existing = list(cursor.fetchall())
        if existing == []:
            patient_id = get_random_str(8)
            query = f'insert into patients (patient_id, doctor_email, patient_name, email, phone, address, age, sex, insurance, apartment_number, dob) values ("{patient_id}", "{doctor_email}", "{patient_name}", "{email}", "{phone}", "{address}", {age}, {sex}, "{insurance}", "{apartment_number}", "{dob}");'
            cursor.execute(query)
            self.connection.commit()
            return patient_id
        else:
            return existing[0]["patient_id"]

    def patient_dropdown(self, doctor_email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            f'select * from patients where doctor_email="{doctor_email}"')

        patients = list(cursor.fetchall())

        final = []
        for patient in patients:
            final.append({"label": patient["patient_name"], "value": patient})

        return [{"options": [{"label": "Add New Patient", "value": "Add New Patient"}]},
                {"label": "Select Patient", "options": final}]

    def get_patients(self, doctor_email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            f'select * from patients where doctor_email="{doctor_email}"')

        patients = list(cursor.fetchall())
        return patients

    def delete_patient(self, patient_id):
        cursor = self.connection.cursor()

        cursor.execute(f'delete from patients where patient_id="{patient_id}"')
        self.connection.commit()

    def update_schedule(self, day, email, start, end):
        cursor = self.connection.cursor()

        cursor.execute(
            "update nurses\nset monday_start=-1, monday_end=-1, tuesday_start=-1, tuesday_end=-1, wednesday_start=-1, wednesday_end=-1, thursday_start=-1, thursday_end=-1, friday_start=-1, friday_end=-1, saturday_start=-1, saturday_end=-1, sunday_start=-1, sunday_end=-1\nwhere 1 = 1;")

        for i in range(0, len(day)):
            x = "update nurses\nset " + day[i].lower() + "_start=" + str(start[i]) + ", " + day[i].lower(
            ) + "_end=" + str(end[i]) + "\nwhere email=\"" + email[i] + "\";"
            cursor.execute(x)
        self.connection.commit()

    def update_details(self, mrn, height, weight, blood_pressure, spo2, heart_rate, respiratory_rate, temperature,
                       visit_duration):
        bmi = calculate_bmi(weight, height)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn = "{mrn}"')
        details = cursor.fetchall()[0]

        age = details["age"]

        sex = details["sex"]

        phone = details["phone"]
        if sex == SEX_MALE:
            wp = get_percentile(0, 0, int(age), float(weight))
            hp = get_percentile(0, 1, int(age), float(height))
            bmip = get_percentile(0, 2, int(age), float(bmi))
        else:
            wp = get_percentile(1, 0, int(age), int(weight))
            hp = get_percentile(1, 1, int(age), int(height))
            bmip = get_percentile(1, 2, int(age), float(bmi))

        x = (
            f'update visits\nset visit_status=1, visit_duration={visit_duration}, bmi={bmi}, height={height}, weight={weight},'
            f'blood_pressure="{blood_pressure}", spo2={spo2}, heart_rate={heart_rate}, respiratory_rate={respiratory_rate}, '
            f'temperature={temperature}, height_percentile={hp}, bmi_percentile={bmip}, weight_percentile={wp} \n'
            f'where mrn = "{mrn}"')

        cursor.execute(x)

        try:
            cursor.execute(f'select * from visits where mrn="{mrn}"')
            visit = list(cursor.fetchall())[0]
            sub_id = self.get_subscription_id(visit["doctor_email"])
            stripe.SubscriptionItem.create_usage_record(
                sub_id,
                quantity=1,
                timestamp=int(time.time()),
                action='increment',
            )
        except Exception as e:
            pass

        self.connection.commit()

    def dashboard_finish_visit(self, mrn, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn = "{mrn}"')
        details = cursor.fetchall()[0]
        phone = details["phone"]

        cursor.execute(
            f'update visits set visit_status={value} where mrn="{mrn}"')
        self.connection.commit()
        

    def mobile_finish_visit(self, mrn, timestamp, insurance_id, insurance_name, ssn, passport_number, complaint,
                            number_of_lines):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where mrn = "{mrn}"')
        details = cursor.fetchall()[0]
        phone = details["phone"]

        cursor.execute(f'select * from visits where order_id != -1;')

        order_id = 10000 + len(list(cursor.fetchall()))

        accession_number = accession_number = randint(10000000, 99999999)

        if ssn != "" or insurance_id != "" or insurance_name != "":
            self.upload_sftp(mrn, ssn, insurance_id, insurance_name,
                             order_id, timestamp, accession_number)

        insurance_str = ""
        if insurance_id == "" or insurance_name == "":
            if ssn == "":
                insurance_str = f'{insurance_id}, {insurance_name}'
            else:
                insurance_str = f'{insurance_id}, {insurance_name}, SSN Provided'
        else:
            insurance_str = ","

        pdf_file = BytesIO()
        canvas = Canvas(pdf_file, pagesize=A4)

        name = details["patient_name"]
        dob = f'{details["dob_month"]}/{details["dob_date"]}/{details["dob_year"]}'

        client_id = "21088"
        canvas.setFont("Courier-Bold", 18)
        canvas.drawString(2 * cm, 27.4 * cm, "PATIENT REQUISITION ENTRY")

        canvas.setFont("Courier", 16)
        canvas.drawString(2 * cm, 26.4 * cm, f'Name: {name}')
        canvas.drawString(2 * cm, 25.4 * cm, f'DOB: {dob}')
        canvas.drawString(2 * cm, 24.4 * cm, f'Order ID: {order_id}')
        canvas.drawString(2 * cm, 23.4 * cm, f'Client ID: {client_id}')
        canvas.save()
        pdf_data = pdf_file.getvalue()
        push_label_to_s3(pdf_data, mrn + "/label/")
        cursor.execute(
            f'update visits set visit_status=1, chief_complaint="{complaint}", completed_timestamp="{str(timestamp)}", number_of_lines={number_of_lines}, passport_number="{passport_number}", insurance="{insurance_id + "," + insurance_name}", order_id={order_id}, accession_number={accession_number} where mrn="{mrn}"')
        self.connection.commit()

    def update_chief_complaint(self, mrn, new):
        cursor = self.connection.cursor()
        cursor.execute(
            f'update visits\nset chief_complaint="{new}" \n where mrn="{mrn}"')
        self.connection.commit()

    def update_note_to_patient(self, mrn, new):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(f'select * from visits where mrn="{mrn}"')
        visit = list(cursor.fetchall())[0]

        if visit["note_to_patient"] == "":
            self.send_doctor_notes_email(visit["email"], visit["patient_name"])
        cursor.execute(
            f'update visits\nset note_to_patient="{new}" \n where mrn="{mrn}"')
        self.connection.commit()

    def get_family_members(self, address, name):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        final = []
        cursor.execute(
            f'select * from patients where patient_name != "{name}"')

        visits = list(cursor.fetchall())

        for visit in visits:
            if process(visit["address"]) == process(address):
                final.append(visit)

        return final

    def update_physical_exam_notes(self, mrn, new):
        cursor = self.connection.cursor()
        cursor.execute(
            f'update visits\nset physical_exam_notes="{new}" \n where mrn="{mrn}"')
        self.connection.commit()

    def update_is_insurance_pay(self, mrn, value):
        cursor = self.connection.cursor()
        cursor.execute(
            f'update visits set is_insurance_pay="{value}" where mrn="{mrn}"')
        self.connection.commit()

    def update_is_healthie(self, mrn, healthie):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set is_healthie="{healthie}" where mrn="{mrn}"')
        self.connection.commit()
        return {"status": "success"}

    def update_zoom_link(self, mrn, zoom_link):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set healthie_visit_zoom_link="{zoom_link}" where mrn="{mrn}"')
        self.connection.commit()
        return {"status": "success"}

    def update_is_aysnc(self, email, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set is_async="{value}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_schedule_followup_visit_col_endpoint(self, email, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set first_visit="{value}",schedule_followup_visit="{value}",schedule_first_visit="{value}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_user_pharmacy(self, email,pharmacy,pharmacy_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set pharmacy="{pharmacy}", pharmacy_id="{pharmacy_id}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_user_ccm_rpm(self, email,ccmEligible,ccmCopay,rpmEligible,rpmCopay,rpmCoinsurance):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set ccmEligible="{ccmEligible}", ccmCopay="{ccmCopay}",rpmEligible="{rpmEligible}",rpmCopay="{rpmCopay}",rpmCoinsurance="{rpmCoinsurance}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_airtable_id(self, email, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set airtable_id="{value}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_backup_medicin(self, email, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set backup_medicine="{value}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_caseid(self, email, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set md_case_id="{value}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def update_is_second_lab_order(self, email, value):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                f'update visits set is_second_lab_order="{value}" where email="{email}"')
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

    def update_schedule_value(self, email, schedule):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set schedule_first_visit="{schedule}" where email="{email}"')
        self.connection.commit()
        return {"status": "success"}

    def get_nurse_visits(self, nurse_email, d, m, y):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                f'select * from visits where nurse_email="{nurse_email}"')
            rows = list(cursor.fetchall())

            incomplete_visits = []
            completed_visits = []
            tomorrow = []
            for row in rows:
                patient_sex = "Female" if (
                        row["sex"] == SEX_FEMALE) else "Male"
                tests = []

                if row["urine"] == 1:
                    tests.append({"name": "Urine"})
                if row["strep"] == 1:
                    tests.append({"name": "Strep"})
                if row["flu"] == 1:
                    tests.append({"name": "Flu"})
                if row["covid"] == 1:
                    tests.append({"name": "COVID"})
                if row["viral"] == 1:
                    tests.append({"name": "Viral"})
                if row["blood"]:
                    tests.append({"name": "Blood"})

                x = row
                x["name"] = row["patient_name"]
                x["sex"] = patient_sex
                x["date"] = f'{row["visit_month"]}/{row["visit_date"]}/{row["visit_year"]}'

                x["time"] = row["visit_time"]
                x["notes"] = row["consumer_notes"]
                x["tests"] = tests
                x["is_refunded"] = row["refunded"]
                x["nurse_time"] = str(row["nurse_time"])
                x["doctor_time"] = str(row["visit_time"])
                x["flight_time"] = str(x["flight_time"])

                visit_date = [row["visit_year"],
                              row["visit_month"], row["visit_date"]]
                current_date = [y, m, d]

                if date(visit_date[0], visit_date[1], visit_date[2]) == date(current_date[0], current_date[1],
                                                                             current_date[2]) + timedelta(days=1):
                    tomorrow.append(x)

                if row["visit_status"] == 0:
                    if row["refunded"] == 0 and current_date == visit_date:
                        incomplete_visits.append(x)
                else:
                    if current_date == visit_date and row["refunded"] == 0:
                        completed_visits.append(x)

            incomplete_visits = sorted(
                incomplete_visits, key=lambda k: int(k['nurse_time']))
            tomorrow = sorted(tomorrow, key=lambda k: int(k['nurse_time']))
            completed_visits = sorted(completed_visits, key=lambda k: parse_final_date(
                k["date"]) * 10000 + int(k["nurse_time"]), reverse=True)
            self.connection.commit()
            return {"upcoming": incomplete_visits, "finished": completed_visits, "tomorrow": tomorrow}
        except Exception as e:
            return {"upcoming": [], "finished": []}

    def edit_patient(self, mrn, visit_date, visit_month, visit_year, visit_time, nurse_time, patient_name, email, phone,
                     address, notes,
                     sex, insurance, chief_complaint, urine, strep, flu, covid, ecg, viral, spirometry, blood,
                     apartment_number, doctor_name, dob_date, dob_month, dob_year, requested_tests, zip_code,
                     nurse_email, nurse_name, is_flight):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select * from visits where mrn = \"" + mrn + "\"")
        visit = list(cursor.fetchall())[0]

        age = calculate_age(date(int(dob_year), int(dob_month), int(dob_date)))

        patient_id = visit["patient_id"]

        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        cursor.execute(
            f'update patients set patient_name="{patient_name}", phone="{phone}", age={age}, sex={sex}, apartment_number="{apartment_number}" where patient_id="{patient_id}"')

        # if visit_date != visit["visit_date"] or visit_month != visit["visit_month"] or visit_year != visit["visit_year"] or visit_time != visit["visit_time"]:
        #     sms = f'Hey {visit["patient_name"].split(" ")[0]}! Your remote visit with Dr. {doctor_name} has been rescheduled for {visit_month}/{visit_date}/{visit_year} at {parse_time(visit_time)}. The nurse will arrive at your home at the same time ({parse_time(visit["nurse_time"])}).'

        #     try:
        #         message = twilio_client.messages.create(
        #              body=sms,
        #              from_='+18454069635',
        #              to='+1' + str(visit["phone"]))
        #     except:
        #         print("message failed to send.")

        x = (
            f'update visits\n set visit_date={visit_date}, visit_month={visit_month}, visit_year={visit_year}, visit_time={visit_time}, nurse_time={nurse_time},'
            f'patient_name="{patient_name}", email="{email}", phone="{phone}", address="{address}", notes="{notes}", '
            f'nurse_name="{nurse_name}", nurse_email="{nurse_email}", dob_date={dob_date}, dob_month={dob_month}, dob_year={dob_year}, sex={sex}, insurance="{insurance}", '
            f'chief_complaint="{chief_complaint}", urine={urine}, strep={strep}, flu={flu}, covid={covid}, ecg={ecg}, viral={viral}, '
            f'spirometry={spirometry}, zip_code="{zip_code}", blood={blood}, consumer_notes="{requested_tests}", doctor_name="{doctor_name}", apartment_number="{apartment_number}", age={age}, is_flight={is_flight} \n where mrn="{mrn}"')
        cursor.execute(x)
        self.connection.commit()

    def edit_patient_address(self, mrn, address):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set address="{address}" where mrn="{mrn}";')
        self.connection.commit()
        return {"status": "success"}

    def edit_patient_profile_fake(self, mrn, patient_name, insurance, pharmacy, patient_address, dob_date, dob_month,
                             dob_year, sex, height, weight, current_medications, allergies, region_no, patient_id_md,
                             patient_id, is_user_verified, mobile, symptoms, cartQuestion, tele_health, primary_doc,
                             insurance_payer_id, is_pregnent, isAppleUser, img_url, agreement, apartment_number,
                             address, pharmacyIns,insurance_card_photo,rx_card_photo):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        birthDate = date(dob_year, dob_month, dob_date)
        age = calculate_age(birthDate)

        now = time.time_ns()

        cursor.execute(f'select * from visits where mrn="{mrn}"')
        data = list(cursor.fetchall())[0]

        test = data["consumer_notes"]

        # patient_name = data["patient_name"]

        receipt_email = data["email"]

        if sex == 0:
            final_sex = "M"
        elif sex == 1:
            final_sex = "F"
        else:
            final_sex = "O"
        lab_fax = data["lab_fax"]
        print(mobile)

        if insurance == "No" or insurance == "":
            is_insurance = 0
            provider = "quest"
        else:
            is_insurance = 1
            provider = "quest" if "quest" in address.lower() else "labcorp"

        if isAppleUser == "2":
            if insurance == "No" or insurance == "":
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_without_insurance")
            else:
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_with_insurance")

        cursor.execute(
            f'update visits set patient_name="{patient_name}",insurance="{insurance}", pharmacy="{pharmacy}", patient_address="{patient_address}", dob_date={dob_date}, dob_month={dob_month}, dob_year={dob_year}, age={age}, sex={sex},current_medications="{current_medications}",height="{height}",weight="{weight}",allergies="{allergies}",patient_id_md="{patient_id_md}",patient_id="{patient_id}", is_user_verified="{is_user_verified}", phone="{mobile}",patient_symptoms="{symptoms}",test_year_rc="{cartQuestion}",primary_care_doctor="{primary_doc}",tele_health="{tele_health}",insurance_payer_id="{insurance_payer_id}",is_pregnent="{is_pregnent}",img_url="{img_url}",consent_agreement_val="{agreement}",update_time="{now}",address="{address}",apartment_number="{apartment_number}",pharmacy_ins_patient="{pharmacyIns}",insurance_card_photo={insurance_card_photo},rx_card_photo={rx_card_photo} where email="{receipt_email}";')

        # if provider == "labcorp":
        #     print(generate_labcorp_pdf(test, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))
        # else:
        #     print(generate_quest_pdf(test, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))

        self.connection.commit()

        return {"status": "success"}
    def edit_patient_profile(self, mrn, patient_name, insurance, pharmacy, patient_address, dob_date, dob_month,
                             dob_year, sex, height, weight, current_medications, allergies, region_no, patient_id_md,
                             patient_id, is_user_verified, mobile, symptoms, cartQuestion, tele_health, primary_doc,
                             insurance_payer_id, is_pregnent, isAppleUser, img_url, agreement, apartment_number,
                             address, pharmacyIns):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        birthDate = date(dob_year, dob_month, dob_date)
        age = calculate_age(birthDate)

        now = time.time_ns()

        cursor.execute(f'select * from visits where mrn="{mrn}"')
        data = list(cursor.fetchall())[0]

        test = data["consumer_notes"]

        # patient_name = data["patient_name"]

        receipt_email = data["email"]

        if sex == 0:
            final_sex = "M"
        elif sex == 1:
            final_sex = "F"
        else:
            final_sex = "O"
        lab_fax = data["lab_fax"]
        print(mobile)

        if insurance == "No" or insurance == "":
            is_insurance = 0
            provider = "quest"
        else:
            is_insurance = 1
            provider = "quest" if "quest" in address.lower() else "labcorp"

        if isAppleUser == "2":
            if insurance == "No" or insurance == "":
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_without_insurance")
            else:
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_with_insurance")

        cursor.execute(
            f'update visits set patient_name="{patient_name}",insurance="{insurance}", pharmacy="{pharmacy}", patient_address="{patient_address}", dob_date={dob_date}, dob_month={dob_month}, dob_year={dob_year}, age={age}, sex={sex},current_medications="{current_medications}",height="{height}",weight="{weight}",allergies="{allergies}",patient_id_md="{patient_id_md}",patient_id="{patient_id}", is_user_verified="{is_user_verified}", phone="{mobile}",patient_symptoms="{symptoms}",test_year_rc="{cartQuestion}",primary_care_doctor="{primary_doc}",tele_health="{tele_health}",insurance_payer_id="{insurance_payer_id}",is_pregnent="{is_pregnent}",img_url="{img_url}",consent_agreement_val="{agreement}",update_time="{now}",address="{address}",apartment_number="{apartment_number}",pharmacy_ins_patient="{pharmacyIns}" where email="{receipt_email}";')

        # if provider == "labcorp":
        #     print(generate_labcorp_pdf(test, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))
        # else:
        #     print(generate_quest_pdf(test, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))

        self.connection.commit()

        return {"status": "success"}
    
    def edit_patient_profile_new(self, mrn, patient_name, insurance, pharmacy, patient_address, dob_date, dob_month,
                             dob_year, sex, height, weight, current_medications, allergies, region_no, patient_id_md,
                             patient_id, is_user_verified, mobile, symptoms, cartQuestion, tele_health, primary_doc,
                             insurance_payer_id, is_pregnent, isAppleUser, img_url, agreement, apartment_number,
                             address, pharmacyIns,md_case_id,zip_code,pharmacy_id,about_us,sexual_partner,contrave_issues,test_name):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        birthDate = date(dob_year, dob_month, dob_date)
        age = calculate_age(birthDate)

        now = time.time_ns()

        cursor.execute(f'select * from visits where mrn="{mrn}"')
        data = list(cursor.fetchall())[0]

        test = data["consumer_notes"]

        # patient_name = data["patient_name"]

        receipt_email = data["email"]

        if sex == 0:
            final_sex = "M"
        elif sex == 1:
            final_sex = "F"
        else:
            final_sex = "O"
        lab_fax = data["lab_fax"]
        print(mobile)

        if insurance == "No" or insurance == "":
            is_insurance = 0
            provider = "quest"
        else:
            is_insurance = 1
            provider = "quest" if "quest" in address.lower() else "labcorp"

        if isAppleUser == "2":
            if insurance == "No" or insurance == "":
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_without_insurance")
            else:
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_with_insurance")

        cursor.execute(
            f'update visits set patient_name="{patient_name}",insurance="{insurance}", pharmacy="{pharmacy}", patient_address="{patient_address}", dob_date={dob_date}, dob_month={dob_month}, dob_year={dob_year}, age={age}, sex={sex},current_medications="{current_medications}",height="{height}",weight="{weight}",allergies="{allergies}",patient_id_md="{patient_id_md}",patient_id="{patient_id}", is_user_verified="{is_user_verified}", phone="{mobile}",patient_symptoms="{symptoms}",test_year_rc="{cartQuestion}",primary_care_doctor="{primary_doc}",tele_health="{tele_health}",insurance_payer_id="{insurance_payer_id}",is_pregnent="{is_pregnent}",img_url="{img_url}",consent_agreement_val="{agreement}",update_time="{now}",address="{address}",apartment_number="{apartment_number}",pharmacy_ins_patient="{pharmacyIns}",md_case_id="{md_case_id}",zip_code={zip_code},pharmacy_id="{pharmacy_id}",sexual_partner="{sexual_partner}",about_us="{about_us}",contrave_issues="{contrave_issues}",consumer_notes="{test_name}" where email="{receipt_email}";')

        # if provider == "labcorp":
        #     print(generate_labcorp_pdf(test, ibnt(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))
        # else:
        #     print(generate_quest_pdf(test, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))

        self.connection.commit()

        return {"status": "success","md_id" :patient_id_md,"drchorno_id":patient_id, "case_id":md_case_id}

    def edit_patient_profile_new_fake(
            self,
            mrn,
            patient_name,
            insurance,
            pharmacy,
            patient_address,
            dob_date,
            dob_month,
            dob_year,
            sex,
            height,
            weight,
            current_medications,
            allergies,
            region_no,
            patient_id_md,
            patient_id,
            is_user_verified,
            mobile,
            symptoms,
            cartQuestion,
            tele_health,
            primary_doc,
            insurance_payer_id,
            is_pregnent,
            isAppleUser,
            img_url,
            agreement,
            apartment_number,
            address,
            pharmacyIns,
            md_case_id,
            zip_code,
            pharmacy_id,
            about_us,
            sexual_partner,
            contrave_issues,
            test_name,
            healthie_id,
            insurance_flag,
            tried_metformin,
            plan="no",
            patient_test_type="normal"
    ):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        birthDate = date(dob_year, dob_month, dob_date)
        age = calculate_age(birthDate)
        now = time.time_ns()
        cursor.execute(f'select * from visits where mrn="{mrn}"')
        data = list(cursor.fetchall())[0]
        test = data["consumer_notes"]
        # patient_name = data["patient_name"]
        receipt_email = data["email"]
        if sex == 0:
            final_sex = "M"
        elif sex == 1:
            final_sex = "F"
        else:
            final_sex = "O"
        lab_fax = data["lab_fax"]
        if insurance == "No" or insurance == "":
            is_insurance = 0
            provider = "quest"
        else:
            is_insurance = 1
            provider = "quest" if "quest" in address.lower() else "labcorp"
        if isAppleUser == "2":
            if insurance == "No" or insurance == "":
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_without_insurance")
            else:
                self.send_patient_message(
                    patient_name, "", mobile, "checkout_with_insurance")
        cursor.execute(
            f'update visits set patient_name="{patient_name}",insurance="{insurance}", pharmacy="{pharmacy}", patient_address="{patient_address}", dob_date={dob_date}, dob_month={dob_month}, dob_year={dob_year}, age={age}, sex={sex},current_medications="{current_medications}",height="{height}",weight="{weight}",allergies="{allergies}",patient_id_md="{patient_id_md}",patient_id="{patient_id}", is_user_verified="{is_user_verified}", phone="{mobile}",patient_symptoms="{symptoms}",test_year_rc="{cartQuestion}",primary_care_doctor="{primary_doc}",tele_health="{tele_health}",insurance_payer_id="{insurance_payer_id}",is_pregnent="{is_pregnent}",img_url="{img_url}",consent_agreement_val="{agreement}",update_time="{now}",address="{address}",apartment_number="{apartment_number}",pharmacy_ins_patient="{pharmacyIns}",md_case_id="{md_case_id}",zip_code={zip_code},pharmacy_id="{pharmacy_id}",sexual_partner="{sexual_partner}",about_us="{about_us}",contrave_issues="{contrave_issues}",healthie_id="{healthie_id}",insurance_flag="{insurance_flag}",tried_metformin="{tried_metformin}",plan="{plan}",patient_test_type="{patient_test_type}" where email="{receipt_email}";')
        # if provider == "labcorp":
        #     print(generate_labcorp_pdf(test, ibnt(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))
        # else:
        #     print(generate_quest_pdf(test, int(is_insurance), patient_name, int(dob_month), int(dob_date), int(
        #         dob_year), receipt_email, mobile[-10::], final_sex, str(lab_fax), mrn, insurance, region_no))
        self.connection.commit()
        return {"status": "success", "md_id": patient_id_md, "drchorno_id": patient_id, "case_id": md_case_id}
    
    def edit_email_patient(self, email, old_email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set email="{email}" where email="{old_email}";')

        self.connection.commit()

        return {"status": "success"}
    
    def update_form_patient(self, email, curr_dose):
        try:
            active = 0
            is_checkin_verified = 1
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """UPDATE visits set is_active=%s, curr_dose=%s, is_checkin_verified=%s where email=%s"""
                input_data = (active, curr_dose, is_checkin_verified, email)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            logger.exception(e)
            return {"status": "failure", "message": e}
    
    def update_openloop_customer_id(self, openloop_customer_id, email):
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                query = """update visits set openloop_customer_id=%s where email=%s"""
                input_data = (openloop_customer_id, email)
                logger.info("update_openloop_customer_id: openloop_customer_id=" + str(openloop_customer_id) + " email=" + email)
                cursor.execute(query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            logger.error("update_stripe_openloop_customer_id: " + "openloop_customer_id=" + openloop_customer_id + " email=" + email + " error=" + str(e))
            return {"status": "failure", "message": str(e)}

    def update_pa_results_by_medication(self, name, medication, status):
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                logger.info("update_pa_results_by_medication: name=" + str(name) + " medication=" + str(medication) + " status=" + str(status))

                query = """select email, date_added from pa_results where name = %s;"""
                input_data = (name)
                cursor.execute(query, input_data)
                result = cursor.fetchall()

                if cursor.rowcount == 0:
                    return None

                # check for 6 weeks validity
                most_recent_time = datetime.now() - datetime.timedelta(days = 42)
                index = 0
                most_recent_index = None
                for row in result:
                    # if more recent, assign as most recent
                    if datetime.strptime(row[1], "%Y/%m/%d %H:%M:%S") > most_recent_time:
                        most_recent_time = datetime.strptime(row[1], "%Y/%m/%d %H:%M:%S")
                        most_recent_index = index
                    index = index + 1
                
                # if there is a valid row
                if most_recent_index is not None:
                    preferred_drug_list = ["ozempic", "wegovy", "mounjaro", "saxenda", "rybelsus"]
                    email = result[most_recent_index][0]
                    if medication in preferred_drug_list:
                        # case pa declined
                        if status == "1":
                            # update the medication to be approved in db
                            query_medication = f'update pa_results set {medication}="{status}" where email="{email}"'
                            cursor.execute(query_medication)
                            self.connection.commit()
                            # query for all pa_resuts for the email
                            query_row = f'select * from pa_results where email = "{email}";'
                            logger.info("update_pa_results_by_medication: query=" + str(query_row))
                            cursor.execute(query_row)
                            results = cursor.fetchall()
                            # check if all of the medications are denied
                            if results[0][4] == 1 and  results[0][5] == 1 and results[0][6] == 1 and results[0][7] == 1 and results[0][8] == 1:
                                query_rejected = f'update pa_results set rejected_all = "{1}" where email = "{email}"'
                                cursor.execute(query_rejected)
                            self.connection.commit()
                            # return results
                            return {"mrn": results[0][1], "email": results[0][1], "name": results[0][1], "date_added": results[0][1],"mounjaro": results[0][4], "ozempic": results[0][5], "rybelsus": results[0][6], "saxenda": results[0][7], "wegovy": results[0][8], "preferred_drug_approved": results[0][9], "rejected_all": results[0][10], "date_started": results[0][11]}

                        # case pa approved
                        elif status == "2":
                            # update the medication to be approved in db
                            query_medication = f'update pa_results set {medication}="{status}" where email="{email}"'
                            logger.info("update_pa_results_by_medication: query=" + str(query_medication))
                            cursor.execute(query_medication)
                            self.connection.commit()
                            # query for all pa_resuts for the email
                            query_row = f'select * from pa_results where email = "{email}";'
                            logger.info("update_pa_results_by_medication: query=" + str(query_row))
                            cursor.execute(query_row)
                            results = cursor.fetchall()
                            # return results
                            return {"mrn": results[0][1], "email": results[0][1], "name": results[0][1], "date_added": results[0][1],"mounjaro": results[0][4], "ozempic": results[0][5], "rybelsus": results[0][6], "saxenda": results[0][7], "wegovy": results[0][8], "preferred_drug_approved": results[0][9], "rejected_all": results[0][10], "date_started": results[0][11]}

                        # case invalid pa status
                        else:
                            logger.error("update_pa_results_by_medication: error = invalid status")
                            return None

                    else:
                        logger.error("update_pa_results_by_medication: error=invalid medication")
                        return None

                # if there is no valid row in six weeks
                else:
                    logger.error("update_pa_results_by_medication: error=no rows in last 6 weeks for this customer")
                    return None
        except Exception as e:
            logger.error("update_pa_results_by_medication: name=" + str(name) + " medication=" + str(medication) + " status=" + str(status) + " error=" + str(e))
            return None

    def update_weight_loss_medication(self, email, weight_loss_medication):
        try:
            logger.info("update_weight_loss_medication: email=" + str(email) + " medication=" + str(weight_loss_medication))
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """UPDATE visits set weight_medicine_type=%s where email=%s"""
                input_data = (weight_loss_medication, email)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            logger.error("update_weight_loss_medication: email=" + str(email) + " medication=" + str(weight_loss_medication) + " error=" + str(e))
            return {"status": "failure", "message": str(e)}

    def update_is_amazon(self, email, value):
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """UPDATE visits set is_amazon=%s where email=%s"""
                input_data = (value, email)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            logger.exception(e)
            return {"status": "failure", "message": e}

    def update_patient_visits_add_second_payment_card(self, mrn, card):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'update visits set is_second_card="{card}" where mrn="{mrn}";')
        self.connection.commit()
        return {"status": "success"}

    def update_patient_visits_add_home_charged(self, mrn, is_home_charge):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'update visits set is_home_charge="{is_home_charge}" where mrn="{mrn}";')
        self.connection.commit()
        return {"status": "success"}

    def get_patient_intake_logs(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from drchrono_request_logs where email="{email}";')
        self.connection.commit()
        return {"status": "success"}

    def update_patient_visits_add_freshdesk_ticket_id(self, mrn, freshdesk_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'update visits set freshdesk_id="{freshdesk_id}" where mrn="{mrn}";')
        self.connection.commit()
        return {"status": "success"}

    def update_has_reviewed(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        has_reviewed = 1
        cursor.execute(
            f'update visits set has_reviewed="{has_reviewed}" where email="{email}";')
        self.connection.commit()
        return {"status": "success"}

    def update_consumer_notes_chief_complaints(self, mrn, consumer_notes, chief_complaints):
        """
        update consumer notes and chief complaints based on patient mrn
        """
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select consumer_notes, chief_complaint from visits where mrn="{mrn}"')
        existing_visit = cursor.fetchone()

        consumer_notes_to_update, chief_complaint_to_update = '', ''
        if existing_visit:
            consumer_notes_to_update = existing_visit.get('consumer_notes', '')
            chief_complaint_to_update = existing_visit.get('chief_complaint', '')
        if consumer_notes:
            consumer_notes_to_update = consumer_notes
        if chief_complaints:
            chief_complaint_to_update = chief_complaints

        cursor.execute(
            f"""update visits
            set consumer_notes="{consumer_notes_to_update}", chief_complaint="{chief_complaint_to_update}"
            where mrn="{mrn}" """
        )
        self.connection.commit()
        return {"status": "success"}

    def patient_download_req(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        yes = "yes"
        cursor.execute(
            f'update visits set is_req_download="{yes}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}
    
    def patient_cancel_visit(self, email,reason,cancel_reason):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        yes = "yes"
        cursor.execute(
            f'update visits set is_canceled="{yes}",reason="{reason}",cancel_reason="{cancel_reason}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}
    
    def approve_patient(self, approve, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set is_wl_approved="{approve}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}

    def edit_place_order(self, susbcription_id, value):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set place_order="{value}" where payment_id="{susbcription_id}";')

        self.connection.commit()

        return {"status": "success"}

    def edit_subscriptionId_patient(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set subscription_id="{NULL}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}

    def send_mail_subscription(self, email, type):
        self.send_subscription_patient_email(email, type)
        self.connection.commit()
        return {"status": "success"}

    def send_mail_order_conformation(self, email, name, test):
        self.confirmation_order_email(email, name, test)
        self.connection.commit()
        return {"status": "success"}

    def edit_refill_subscriptionId_patient(self, email, refill, subscription_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set subscription_id="{subscription_id}",refill="{refill}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}

    def edit_retest_patient(self, email, retest):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set retest="{retest}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}

    def edit_insurance_patient(self, email):
        val = "No"
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set insurance="{val}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}

    def edit_payment_id(self, subId, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set payment_id="{subId}" where email="{email}";')

        self.connection.commit()

        return {"status": "success"}

    def edit_md_drchrono_id_patient(self, mrn, patient_md_id, patient_derchrono_id, md_case_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'update visits set patient_id_md="{patient_md_id}",patient_id="{patient_derchrono_id}",md_case_id="{md_case_id}" where mrn="{mrn}";')

        self.connection.commit()

        return {"status": "success"}

    def get_patient_profile(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where email="{email}"')

        data = list(cursor.fetchall())

        for i in range(0, len(data)):
            data[i]["sortable_date"] = int(data[i]["booking_year"]) * 100000000 + int(
                data[i]["booking_month"]) * 1000000 + int(data[i]["booking_date"]) * 10000 + int(
                data[i]["booking_time"])

        final = max(data, key=lambda x: x["sortable_date"])

        return {"status": "success", "data": final}

    def get_patient_info(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from visits where email="{email}"')

        data = list(cursor.fetchall())

        for i in range(0, len(data)):
            data[i]["sortable_date"] = int(data[i]["booking_year"]) * 100000000 + int(
                data[i]["booking_month"]) * 1000000 + int(data[i]["booking_date"]) * 10000 + int(
                data[i]["booking_time"])

        final = max(data, key=lambda x: x["sortable_date"])

        return {"status": "success", "data": final}

    def delete_visit(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select * from visits where mrn = \"" + mrn + "\"")
        visit = list(cursor.fetchall())[0]
        # twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # sms = f'Hey, {visit["patient_name"].split(" ")[0]}! Your remote visit scheduled for {visit["visit_month"]}/{visit["visit_date"]}/{visit["visit_year"]} has been cancelled.'

        # try:
        #     message = twilio_client.messages.create(
        #              body=sms,
        #              from_='+18454069635',
        #              to='+1' + str(visit["phone"]))
        # except:
        #     print("message failed to send.")
        cursor.execute(f'delete from visits where mrn = "{mrn}"')
        self.connection.commit()

    def get_table(self, doctor_email, location='all'):

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        if location == "all":
            cursor.execute(
                f'select * from visits where doctor_email="{doctor_email}";')
        else:
            cursor.execute(
                f'select * from visits where doctor_email="{doctor_email}" and location="{location}"')

        rows = list(cursor.fetchall())

        res = []
        for row in rows:

            try:
                f_date = datetime(
                    year=row['visit_year'], month=row['visit_month'], day=row['visit_date']).strftime("%m/%d/%Y")
            except:
                f_date = "NA"

            patient_sex = "Female" if (row['sex'] == SEX_FEMALE) else "Male"

            x = row
            x["name"] = row["patient_name"]
            x["sex"] = patient_sex

            x["dob"] = f'{row["dob_month"]}/{row["dob_date"]}/{row["dob_year"]}'
            x["receipt_email"] = row["email"]
            x["requested_tests"] = row["consumer_notes"]
            x["exact_nurse_time"] = row["nurse_time"]
            x["parsed_exact_nurse_time"] = parse_time(row["nurse_time"])
            x["flight_timestamp"] = row["flight_time"]
            x["complaint"] = row["chief_complaint"]
            x["date"] = f_date
            x["time"] = str(row['visit_time'])

            if int(row["nurse_time"] / 100) % 2 == 0:
                x["nurse_time"] = parse_time(int(
                    (row["nurse_time"]) / 100) * 100) + " - " + parse_time(int((row["nurse_time"]) / 100) * 100 + 200)
            else:
                x["nurse_time"] = parse_time(int(
                    (row["nurse_time"]) / 100) * 100 - 100) + " - " + parse_time(
                    int((row["nurse_time"]) / 100) * 100 + 100)
            res.append(x)

        self.connection.commit()

        return res

    def get_table_test(self, doctor_email, location):

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        if location == "all":
            cursor.execute(
                f'select * from visits where doctor_email="{doctor_email}";')

        else:
            cursor.execute(
                f'select * from visits where doctor_email="{doctor_email}" and location="{location}"')

        rows = list(cursor.fetchall())

        res = []
        for row in rows:

            try:
                f_date = datetime(
                    year=row['visit_year'], month=row['visit_month'], day=row['visit_date']).strftime("%m/%d/%Y")
            except:
                f_date = "NA"

            patient_sex = "Female" if (row['sex'] == SEX_FEMALE) else "Male"

            x = row
            x["name"] = row["patient_name"]
            x["sex"] = patient_sex

            x["dob"] = f'{row["dob_month"]}/{row["dob_date"]}/{row["dob_year"]}'
            x["receipt_email"] = row["email"]
            x["requested_tests"] = row["consumer_notes"]
            x["exact_nurse_time"] = row["nurse_time"]
            x["parsed_exact_nurse_time"] = parse_time(row["nurse_time"])
            x["flight_timestamp"] = row["flight_time"]
            x["complaint"] = row["chief_complaint"]
            x["date"] = f_date
            x["time"] = str(row['visit_time'])

            if int(row["nurse_time"] / 100) % 2 == 0:
                x["nurse_time"] = parse_time(int(
                    (row["nurse_time"]) / 100) * 100) + " - " + parse_time(int((row["nurse_time"]) / 100) * 100 + 200)
            else:
                x["nurse_time"] = parse_time(int(
                    (row["nurse_time"]) / 100) * 100 - 100) + " - " + parse_time(
                    int((row["nurse_time"]) / 100) * 100 + 100)
            res.append(x)

        self.connection.commit()

        return res

    def get_calendar(self, doctor_email, location, start_date, start_month, start_year, end_date, end_month, end_year):

        start_datetime = date(start_year, start_month,
                              start_date) - timedelta(days=7)
        end_datetime = date(end_year, end_month, end_date) + timedelta(days=7)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select * from visits where doctor_email="{doctor_email}" and location="{location}" and ((visit_month={start_datetime.month} and visit_year={start_datetime.year} and visit_date >= {start_datetime.day}) or (visit_month={end_datetime.month} and visit_year={end_datetime.year} and visit_date <= {end_datetime.day}));')

        rows = list(cursor.fetchall())

        res = []
        for row in rows:
            # print(start_date, start_month, start_year, end_date, end_month, end_year, row["visit_year"], row["visit_month"], row["visit_date"])
            visit_datetime = date(
                row["visit_year"], row["visit_month"], row["visit_date"])

            if visit_datetime >= start_datetime and visit_datetime < end_datetime:
                try:
                    f_date = datetime(
                        year=row['visit_year'], month=row['visit_month'], day=row['visit_date']).strftime("%m/%d/%Y")
                except:
                    f_date = "NA"

                patient_sex = "Female" if (
                        row['sex'] == SEX_FEMALE) else "Male"

                x = row
                x["name"] = row["patient_name"]
                x["sex"] = patient_sex

                x["dob"] = f'{row["dob_month"]}/{row["dob_date"]}/{row["dob_year"]}'
                x["receipt_email"] = row["email"]
                x["requested_tests"] = row["consumer_notes"]
                x["exact_nurse_time"] = row["nurse_time"]
                x["parsed_exact_nurse_time"] = parse_time(row["nurse_time"])
                x["flight_timestamp"] = row["flight_time"]
                x["complaint"] = row["chief_complaint"]
                x["date"] = f_date
                x["time"] = str(row['visit_time'])

                if int(row["nurse_time"] / 100) % 2 == 0:
                    x["nurse_time"] = parse_time(int(
                        (row["nurse_time"]) / 100) * 100) + " - " + parse_time(
                        int((row["nurse_time"]) / 100) * 100 + 200)
                else:
                    x["nurse_time"] = parse_time(int(
                        (row["nurse_time"]) / 100) * 100 - 100) + " - " + parse_time(
                        int((row["nurse_time"]) / 100) * 100 + 100)
                res.append(x)

        self.connection.commit()

        return res

    def get_modal_data(self, mrn):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f'select * from results where mrn="{mrn}"')

        results = list(cursor.fetchall())

        file_data = []

        for i in results:
            file_data.append({"name": i["file_name"], "data": i["pdf"]})

        cursor.execute(f'select * from patient_logs where mrn="{mrn}"')
        patient_logs = list(cursor.fetchall())

        return {"file_data": file_data, "patient_logs": patient_logs}

    def add_to_emr(self, mrn):
        cursor = self.connection.cursor()
        cursor.execute(f'update visits\nset mobile=0\nwhere mrn="{mrn}"')
        self.connection.commit()

    def add_doctor_name(self, practice_email, name, doctor_email, account_type):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute(f'select * from doctors where email="{doctor_email}"')

        if account_type == "doctor":
            t = 0
        elif account_type == "staff":
            t = 1
        elif account_type == "customer_service":
            t = 2
        else:
            t = 3

        if list(cursor.fetchall()) != []:
            return
        cursor.execute(
            f'insert into doctors (name, email, admin, type) values ("{name}", "{doctor_email}", "{practice_email}", {t});')
        try:
            signup_user(doctor_email, name)
        except Exception as e:
            pass
        self.connection.commit()

    def delete_doctor_name(self, practice_email, doctor_email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'delete from doctors where admin="{practice_email}" and email="{doctor_email}"')
        self.connection.commit()

    def get_doctor_names(self, practice_email, location):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f'select * from doctors where admin="{practice_email}";')
        doctors = list(cursor.fetchall())

        for j in range(0, len(doctors)):
            if doctors[j]["type"] == 0:
                doctors[j]["type"] = "Doctor"
            elif doctors[j]["type"] == 1:
                doctors[j]["type"] = "Staff"

            elif doctors[j]["type"] == 2:
                doctors[j]["type"] = "Customer Service"
            else:
                doctors[j]["type"] = "Admin"
        final = []
        for i in doctors:
            if i["type"] == "Doctor":
                final.append({"label": i["name"], "value": i["name"]})

        cursor.execute(
            f'select * from nurses where doctor_email="{practice_email}" and location="{location}";')
        n = list(cursor.fetchall())
        nurses = []

        for i in n:
            nurses.append({"label": i["name"], "value": {
                "name": i["name"], "email": i["email"]}})

        return [{"label": "Select Doctor", "options": final}], doctors, nurses
        self.connection.commit()

    def get_edit_data(self, mrn, email, location):

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"select * from visits where mrn = \"{mrn}\"")

        kk = list(cursor.fetchall())[0]

        db_data = kk

        db_data["exact_nurse_time"] = db_data["nurse_time"]

        if int(kk["nurse_time"] / 100) % 2 == 0:
            db_data["nurse_time"] = parse_time(int(
                (kk["nurse_time"]) / 100) * 100) + " - " + parse_time(int((kk["nurse_time"]) / 100) * 100 + 200)
        else:
            db_data["nurse_time"] = parse_time(int(
                (kk["nurse_time"]) / 100) * 100 - 100) + " - " + parse_time(int((kk["nurse_time"]) / 100) * 100 + 100)

        db_data["requested_tests"] = db_data["consumer_notes"]
        db_data["doctor_names"] = self.get_doctor_names(
            kk["doctor_email"], location)

        cursor.execute(
            f'select * from nurses where doctor_email="{kk["doctor_email"]}" and location="{location}"')
        nurses = list(cursor.fetchall())

        all_nurses = [{"label": "Available Nurses", "options": []}]

        for i in nurses:
            all_nurses[0]["options"].append({"label": i["name"], "value": i})

        db_data["all_nurses"] = all_nurses
        self.connection.commit()
        if email != kk["doctor_email"]:
            return 0
        return db_data

    def get_email_from_case(self, case_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            f"select * from visits where md_case_id = \"{case_id}\"")
        data = list(cursor.fetchall())[0]
        return {"data": data}

    def get_subscription_email(self, email):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"select * from subscription where email = \"{email}\"")
        data = list(cursor.fetchall())[0]
        return {"data": data}

    def get_drchrono_lab_orders(self):
        """get all drchrono lab_orders."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT * FROM drchrono_lab_orders"""
                cursor.execute(sql_query)
            return {"status": "success", "data": list(cursor.fetchall())}
        except Exception as e:
            return {"status": "failure", "message": e, "data": []}

    def delete_drchrono_lab_orders(self, lab_order_id, visit_id):
        """delete row from drchrono_lab_orders."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """delete from drchrono_lab_orders where lab_order_id=%s and visit_id=%s"""
                input_data = (lab_order_id, visit_id)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def is_valid_uuid(value):
        print(value)
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    def insert_drchrono_lab_orders(self, lab_order_id, visit_id):
        """insert row into drchrono_lab_orders."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """INSERT INTO drchrono_lab_orders (lab_order_id, visit_id) VALUES (%s, %s)"""
                input_data = (lab_order_id, visit_id)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_results(self, results: str, mrn: str):
        """Update visits table row with results."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_results=%s where mrn=%s"""
                input_data = (results, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_status(self, status: str, mrn: str):
        """Update visits table row with status."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_status=%s where mrn=%s"""
                input_data = (status, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_drchrono_res(self, res: str, ts: str, mrn: str):
        """Update visits table row with res."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_res=%s, drchrono_res_ts=%s  where mrn=%s"""
                input_data = (res, ts, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_drchrono_res_s3_url(self, res: str, mrn: str):
        """Update visits table row with res."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_res=%s where mrn=%s"""
                input_data = (res, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_drchrono_req(self, req: str, ts: str, mrn: str):
        """Update visits table row with req."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_req=%s, drchrono_req_ts=%s where mrn=%s"""
                input_data = (req, ts, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_drchrono_result_notify(self, mrn: str, sent=True):
        """Update visits table row with drchrono_result_notify."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_result_notify=%s where mrn=%s"""
                if sent:
                    input_data = ('sent', mrn)
                else:
                    input_data = ('not', mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_drchrono_result_to_mdint(self, mrn: str, sent=True):
        """Update visits table row with drchrono_result_to_mdint."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_result_to_mdint=%s where mrn=%s"""
                if sent:
                    input_data = ('sent', mrn)
                else:
                    input_data = ('not', mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_md_case_id(self, mrn: str, md_case_id: str):
        """Update visits table row with md_case_id."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set md_case_id=%s where mrn=%s"""
                input_data = (md_case_id, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def get_visits_by_patient_id_date(self, patient_drchrono_id, year, mon, day):
        """get visits by patient_id & date."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT * FROM visits WHERE patient_id=%s AND visit_year=%s AND visit_month=%s AND visit_date=%s"""
                input_data = (patient_drchrono_id, year, mon, day)
                cursor.execute(sql_query, input_data)
            return {"status": "success", "data": list(cursor.fetchall())}
        except Exception as e:
            return {"status": "failure", "message": e, "data": []}

    def get_visits_by_patient_id(self, patient_drchrono_id):
        """get visits by patient_id & returns first visit."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT * FROM visits WHERE patient_id=%s"""
                cursor.execute(sql_query, (patient_drchrono_id))
            return {"status": "success", "data": cursor.fetchone()}
        except Exception as e:
            return {"status": "failure", "message": e, "data": {}}

    def get_visits_all_rows_by_patient_id(self, patient_drchrono_id):
        """get visits by patient_id & returns first visit."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT * FROM visits WHERE patient_id=%s"""
                cursor.execute(sql_query, (patient_drchrono_id))
            return cursor.fetchall()
        except Exception as e:
            logger.exception(e)
            return []

    def get_visits_by_mrn(self, mrn):
        """get visits by mrn & returns first visit."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT * FROM visits WHERE mrn=%s"""
                cursor.execute(sql_query, (mrn))
            return cursor.fetchone()
        except Exception as e:
            return {}

    def get_visits_by_case_id(self, md_case_id: str):
        """get visits by md_case_id"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT mrn, email, is_home_charge FROM visits WHERE md_case_id=%s"""
                cursor.execute(sql_query, (md_case_id))
            return list(cursor.fetchall())
        except Exception as e:
            logger.exception("get_visits_by_case_id => " + str(e))
            return []

    def get_lab_order_results(self, patient_id=None):
        """get lab order results by patient_id or all."""
        if patient_id:
            sql_query = f"""SELECT mrn, patient_id, drchrono_status, drchrono_results FROM visits WHERE patient_id='{patient_id}' """
        else:
            sql_query = """SELECT mrn, patient_id, drchrono_status, drchrono_results FROM visits"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return {"status": "success", "data": list(cursor.fetchall())}
        except Exception as e:
            return {"status": "failure", "message": e, "data": []}

    def update_visits_drchrono_abnormal_tests(self, tests: str, mrn: str):
        """Update visits table row with drchrono_abnormal_tests."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = """update visits set drchrono_abnormal_tests=%s where mrn=%s"""
                input_data = (tests, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def get_not_verified_patients_from_visits(self):
        """get not verified patients from visits table."""
        sql_query = """SELECT patient_name, phone, server_date_time, email
        FROM visits WHERE is_user_verified is NULL OR is_user_verified <> 1"""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            return []

    def get_weightloss_patients(self):
        """get weight loss patients."""
        sql_query = """SELECT * FROM visits WHERE `consumer_notes` = "Ozempic® Weight Loss Program" OR `consumer_notes` = "GLP-1 Weight Loss Program" OR `consumer_notes` = "GLP-1 Weight Loss Complete Program" OR `consumer_notes` = "Naltrexone & Bupropion Program" OR `consumer_notes` = "Rybelsus GLP 1 Tablets" OR  `consumer_notes` = "Saxenda GLP 1 Injections" """
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            return []      

    def get_accutane_patients(self):
        """get weight loss patients."""
        sql_query = """SELECT * FROM visits WHERE `consumer_notes` = "Accutane Acne Complete Program" OR `consumer_notes` = "Accutane Acne Program" """
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            return []

    def make_patient_checkin(self, email, month):
        """get weight loss patients."""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """UPDATE visits SET is_checkin_verified=0, is_active=1, weight_loss_month=%s WHERE email=%s"""
                cursor.execute(sql_query, (month, email))
            self.connection.commit()
            return {"status": "success", "message": "weight loss entry updated"}
        except Exception as e:
            logger.exception(e)
            return {"status": "failure", "message": e}

    def get_not_checked_in_patients_from_visits(self):
        """get not checked in patients from visits table."""
        sql_query = """SELECT patient_name, phone, email
        FROM visits WHERE is_checkin_verified = 0 """
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            logger.exception(e)
            return []

    def mark_checkin_verified(self, email: str):
        """
        Update visits row to mark checkin as verified.
        """
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """UPDATE visits set is_checkin_verified=1 WHERE email=%s"""
                cursor.execute(sql_query, (email))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def insert_notifications(self, phone):
        """insert row into notifications."""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """INSERT INTO notifications (phone, text_sent) VALUES (%s, 0)"""
                cursor.execute(sql_query, (phone,))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def increment_notifications_text_sent(self, phone):
        """update row into notifications."""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = f"""UPDATE notifications SET text_sent = text_sent + 1
                 WHERE phone='{phone}' """
                cursor.execute(sql_update_query)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def get_notifications_text_sent(self, phone):
        """get number of text notifications sent. if exception then return 3."""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = f"""SELECT text_sent FROM notifications WHERE phone='{phone}' """
                res = cursor.execute(sql_query)
                if res == 0:
                    return -1
                result = dict(cursor.fetchone())
                return result.get("text_sent", 0)
        except Exception as e:
            return 3

    def insert_curexa_order(self, email, order_id, status=None):
        """insert into database"""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """INSERT INTO curexa_orders (email, order_id, status) VALUES (%s, %s, %s)"""
                cursor.execute(sql_query, (email, order_id, status))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_curexa_order(self, order_id, status, status_details, carrier, tracking_number):
        """update into database"""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """UPDATE curexa_orders SET status=%s, status_details=%s, carrier=%s, tracking_number=%s where order_id=%s"""
                cursor.execute(sql_query, (status, status_details,
                                           carrier, tracking_number, order_id))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def get_curexa_order(self, email=None, order_id=None):
        """get curexa order results by order_id or email."""
        if order_id is not None and email is not None:
            sql_query = f"""SELECT order_id, status, carrier, tracking_number FROM curexa_orders WHERE order_id='{order_id}' and email='{email}'"""
        elif email is not None:
            sql_query = f"""SELECT order_id, status, carrier, tracking_number FROM curexa_orders WHERE email='{email}'"""
        else:
            sql_query = f"""SELECT * FROM curexa_orders WHERE order_id='{order_id}'"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return {"status": "success", "data": list(cursor.fetchall())}
        except Exception as e:
            return {"status": "failure", "message": e, "data": []}

    def update_subscription_status(self, subscription_status, subscription_id):
        cursor = self.connection.cursor()
        x = f'update visits\nset subscription_status = "{subscription_status}"\nwhere subscription_id = "{subscription_id}"'
        cursor.execute(x)
        self.connection.commit()
        
    def update_subscription_time_status(self, time, subscription_id):
        cursor = self.connection.cursor()
        x = f'update visits\nset server_date_time = "{time}"\nwhere subscription_id = "{subscription_id}"'
        cursor.execute(x)
        self.connection.commit()

    def add_weight_loss_queue_entry(self, email, subscription_id, subscription_type, date_purchased, last_refill_date,
                                    maximum_refills, refill_count, status, remark):
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """INSERT INTO weight_loss_queue 
                (email, subscription_id, subscription_type, date_purchased, last_refill_date,
                maximum_refills, refill_count, status, remark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql_query, (email, subscription_id, subscription_type, date_purchased, last_refill_date,
                                           maximum_refills, refill_count, status, remark))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def get_weight_loss_queues(self):
        sql_query = f"""SELECT * FROM weight_loss_queue"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            return {"status": "failure", "message": e, "data": []}

    def update_weight_loss_queues(self, last_refill_date, order_count, wid):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = (
                f'UPDATE weight_loss_queue SET last_refill_date="{last_refill_date}", order_count="{order_count}" WHERE id="{wid}" ;')
            cursor.execute(query)
            self.connection.commit()
            return {"status": "success", "message": "weight loss entry updated"}
        except Exception as e:
            return {"status": "error", "message": e}

    def delete_weight_loss_queue_entry(self, wid):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            query = (f'DELETE FROM weight_loss_queue WHERE id="{wid}" ;')
            cursor.execute(query)
            self.connection.commit()
            return {"status": "success", "message": "weight loss entry updated"}
        except Exception as e:
            return {"status": "error", "message": e}

    def get_visits_by_subscription_id(self, subscription_id):
        """get visits by subscription_id."""
        if subscription_id is None:
            return []
        else:
            sql_query = f"""SELECT * FROM visits WHERE payment_id='{subscription_id}'"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            logger.exception(e)
            return []

    def insert_retest_visits(self, test_name, data):
        """Insert new row with current date"""
        date_now = datetime.now()
        data["mrn"] = get_random_str(8)
        data["visit_date"] = date_now.day
        data["visit_month"] = date_now.month
        data["visit_year"] = date_now.year
        data["consumer_notes"] = test_name
        data["booking_date"] = data["visit_date"]
        data["booking_month"] = data["visit_month"]
        data["booking_year"] = data["visit_year"]
        data["drchrono_status"] = None
        data["drchrono_results"] = None
        data["server_date_time"] = date_now.strftime('%d/%m/%Y %H:%M:%S')
        data["drchrono_res"] = None
        data["drchrono_req"] = None
        data["drchrono_result_notify"] = None
        data["drchrono_result_to_mdint"] = None
        data["drchrono_res_ts"] = None
        data["drchrono_req_ts"] = None
        data["drchrono_abnormal_tests"] = None
        data["refill"] = "yes"

        try:
            cols = tuple(data.keys())
            col_names = ",".join(cols)
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_insert_query = "INSERT INTO visits (" + col_names + ") VALUES (" + "%s," * (len(cols) - 1) + "%s)"
                input_data = tuple(data.values())
                cursor.execute(sql_insert_query, input_data)
            self.connection.commit()
            logger.info(f"Insert into visits successful: mrn={data['mrn']}, email={data['mrn']}, test="
                        f"data['consumer_notes'], subscription={data['payment_id']}")
            try:
                if data["phone"] != "":
                    if data["address"].lower().startswith("home"):
                        self.send_patient_message(
                            data["patient_name"], "", data["phone"], "checkout_with_home")
                    elif data["insurance"].lower() == "no":
                        self.send_patient_message(
                            data["patient_name"], "", data["phone"], "checkout_without_insurance")
                    else:
                        self.send_patient_message(
                            data["patient_name"], "", data["phone"], "checkout_with_insurance")
            except Exception as e:
                logger.exception(e)
            '''try:
                if is_prod is True and data["email"] != "veergadodia24@gmail.com" and data["email"] != \
                        "nand.vinchhi@gmail.com" and data["email"] != "smart1@gmail.com":
                    self.send_email_on_booking_new(
                        city=data["address"],
                        date=f'{data["visit_month"]}/{data["visit_date"]}/{data["visit_year"]}',
                        time=parse_time(data["nurse_time"]),
                        options=data["options"], ["rob@joinnextmed.com", ], path=data["email"], price=data["price"], name="Rob/Frank")
                    self.send_email_on_booking_new(address, f'{visit_month}/{visit_date}/{visit_year}', parse_time(
                            nurse_time), options, "frank@joinnextmed.com", path, total_price, "Frank")

            except Exception as e:
                logger.exception(e)'''
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Insert into visits failed: mrn={data['mrn']}, email={data['mrn']}, test="
                         f"data['consumer_notes'], subscription={data['payment_id']}")
            logger.exception(e)
            return {"status": "failure", "message": e}

    def insert_healthie_patient(self, user_id, email):
        """insert into healthie"""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """INSERT INTO healthie (user_id, email) VALUES (%s, %s)"""
                cursor.execute(sql_query, (user_id, email))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def update_visits_email(self, email, new_email):
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """UPDATE visits SET email=%s where email=%s"""
                updated = cursor.execute(sql_query, (new_email, email))
            self.connection.commit()
            logger.info(f"update_visits_email from {email} to {new_email} ==> {updated}")
            return updated
        except Exception as e:
            logger.exception(f"update_visits_email ==> {str(e)}")
            return False

    def update_visits_phone(self, email, new_phone):
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """UPDATE visits SET phone=%s where email=%s"""
                updated = cursor.execute(sql_query, (new_phone, email))
            self.connection.commit()
            logger.info(f"update_visits_phone {new_phone} for {email} ==> {updated}")
            return updated
        except Exception as e:
            logger.exception(f"update_visits_email ==> {str(e)}")
            return False
    
    def insert_spreadsheet_data(self, is_patient_eligible, copay_amount, coinsurance_percentage):
        """insert into database"""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """INSERT INTO spreadsheet_data (is_patient_eligible, copay_amount, coinsurance_percentage) VALUES (%s, %s, %s)"""
                cursor.execute(sql_query, (is_patient_eligible, copay_amount, coinsurance_percentage))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def intake_add_eligibility(
            self, date_requested, is_patient_policy_holder, first_name, last_name, insurance_carrier,
            insurance_member_id, insurance_group_member, dob, email, policy_holder_first_name,
            policy_holder_last_name, policy_holder_dob, is_patient_eligible, copay_amount,
            coinsurance_percentage
    ):
        """insert into database"""
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """INSERT INTO intake_eligibility (
                               date_requested, is_patient_policy_holder, first_name, last_name, insurance_carrier,
                               insurance_member_id, insurance_group_member, dob, email, policy_holder_first_name, 
                               policy_holder_last_name, policy_holder_dob, is_patient_eligible, copay_amount, 
                               coinsurance_percentage
                               ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql_query, (date_requested, is_patient_policy_holder, first_name, last_name,
                                           insurance_carrier, insurance_member_id, insurance_group_member, dob, email,
                                           policy_holder_first_name, policy_holder_last_name, policy_holder_dob,
                                           is_patient_eligible, copay_amount, coinsurance_percentage))
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "message": e}

    def add_drchrono_request_log(self, data, environment):
        """
        add drchrono request log
        """
        try:
            data["ins_data"]["primary_insurance"]["photo_front"] = ""
        except KeyError:
            pass
        record_id = 0
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = "INSERT INTO `drchrono_request_logs` (`email`, `request_params`, `environment`) VALUES (%s, %s, %s)"
            try:
                cursor.execute(query, (data['email'], json.dumps(data), environment))
                record_id = cursor.lastrowid
                self.connection.commit()
            except:
                self.connection.rollback()
                return {"status": "failure"}
        return {"status": "success", "record_id": record_id}

    def update_drchrono_request_log_processed(self, log_id, processed):
        """
        update drchrono request log processed field
        """
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = f"update `drchrono_request_logs` set processed={processed} where id={log_id}"
            cursor.execute(query)
            try:
                self.connection.commit()
            except:
                self.connection.rollback()
                return {"status": "failure"}
        return {"status": "success"}

    def get_amazon_seller_queues(self):
        """
        Get unprocessed data from amazon seller table
        """
        sql_query = f"""SELECT * FROM amazon_seller where processed=0"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return list(cursor.fetchall())
        except Exception as e:
            logger.exception("get_amazon_seller_queues => " + str(e))
            return {"status": "failure", "message": e, "data": []}

    def update_amazon_seller_processed(
            self, amazon_seller_id, product_name,
            mrn, product_quantity, address
    ):
        """
        Update processed column in amazon seller and add
        product_name and is_amazon in visits.
        """
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                amazon_seller = (f'update amazon_seller\nset processed = 1\nwhere id="{amazon_seller_id}"')
                cursor.execute(amazon_seller)
                visits = (f'update visits\nset product_name = "{product_name}", product_quantity = "{product_quantity}", patient_address="{address}", is_amazon = 1\nwhere mrn="{mrn}"')
                cursor.execute(visits)
            self.connection.commit()
            return {"status": "success"}
        except Exception as e:
            logger.exception("create_visits_from_amazon_seller => " + str(e))
            return {"status": "failure", "message": str(e)}

    def health_check_db(self):
        """Check is the db server is alive."""
        try:
            self.connection.ping()
            return True
        except Exception as e:
            return False

    def fetch_pid(self, pid):
        try:
            sql_query = f"""SELECT * FROM pid where pid={pid}"""
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            return cursor.fetchone()
        except Exception as e:
            logger.exception("fetch_pid => " + str(e))
            return {"status": "failure", "message": e, "data": []}

    def get_visits_all_records(self):
        """get all visits data"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = """SELECT * FROM visits"""
                cursor.execute(sql_query)
            return cursor.fetchall()
        except Exception as e:
            logger.exception(e)
            return []

    def add_user_stage_in_process(self, mrn, stage, completed=False):
        """insert into database"""
        stage_id = str(uuid.uuid4())
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = f'INSERT INTO user_stage_in_process (stage_id, mrn, stage, completed)' \
                            f'VALUES ("{stage_id}", "{mrn}", "{stage}", {completed})'
                cursor.execute(sql_query)
            self.connection.commit()
            return True

        except Exception as e:
            return False


    def insert_gogomeds_order(self, AffiliateOrderNumber, gogomed_AffiliateOrderNumber, OrderId):
        try:
            self.connection.ping()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = f'INSERT INTO gogomeds_orders (AffiliateOrderNumber, gogomed_affiliateordernumber, gogomed_orderid)  VALUES ("{AffiliateOrderNumber}", "{gogomed_AffiliateOrderNumber}", "{OrderId}")'
                cursor.execute(sql_query)
            self.connection.commit()
            return True
        except Exception as e:
            return False

    def fetch_patient_from_visits(self, mrn):
        try:
            sql_query = f"""SELECT * FROM visits where mrn='{mrn}'"""
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchone()
                if result:
                    return result
                else:
                    return None
        except Exception as e:
            logger.exception("fetch_patient_from_visits => " + str(e))
            return {"status": "failure", "message": e, "data": []}

    def update_visits_humhealth(self, mrn):
        try:
            sql_query = f"""UPDATE visits SET is_humhealth = {1} where mrn='{mrn}'"""
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql_query)
            self.connection.commit()
        except Exception as e:
            logger.exception("update_visits_humhealth => " + str(e))
            return {"status": "failure", "message": e, "data": []}



def append_to_gsheet(path, price):
    """"""
    try:
        # consider EST timezone
        tz = timezone('EST')
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S-0500")
        parsed_url = urlparse(path)
        gclid = parse_qs(parsed_url.query)['gclid'][0]
        price = int(int(price) / 100)

        spreadsheet_id = '1JnFLEVLcnuLh9N80njtlIJwrgPYbxQFnSVyjQTSG5ng'
        gc = gspread.service_account(filename='./gspread_service.json')
        spreadsheets = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheets.worksheet("Sheet1")

        all_values = worksheet.get_all_values()
        next_row_num = len(all_values) + 1
        # print(next_row_num)

        update_row = [gclid, 'Account - Offline Purchase', now, price, 'USD']
        worksheet.update(f'A{next_row_num}:E{next_row_num}', [update_row])
    except Exception as e:
        print(e)


