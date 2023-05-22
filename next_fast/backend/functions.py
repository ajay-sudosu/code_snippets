import logging
import random
import string
import pymysql
import pandas as pd
import numpy as np
from scipy.stats import norm
from pygrowup import Calculator
from botocore.exceptions import ClientError
from botocore.client import Config
import webbrowser
calculator = Calculator(adjust_height_data=False, adjust_weight_scores=False,
                       include_cdc=True, logger_name='pygrowup',
                       log_level='INFO')
from datetime import date, datetime, timedelta
import boto3
import base64
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
from io import BytesIO
import uuid
from config import DB_ENDPOINT, DB_USERNAME, DB_PASSWORD, DB_NAME, DEFAULT_NURSE_EMAIL
import requests, json
from botocore.exceptions import NoCredentialsError

logger = logging.getLogger("fastapi")

session = boto3.Session(
    aws_access_key_id="AKIAJSZRUVGIPVVOPUGA",
    aws_secret_access_key="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",
)

ACCESS_KEY = 'AKIAJSZRUVGIPVVOPUGA'
SECRET_KEY = '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'
api_key ='AIzaSyAe7nmOwtSLsOdfYwJ_ns3p1krP0h97rPE'

s3 = session.resource("s3")
s3_bucket = s3.Bucket("helio-patient-data")

json_file = open("driving_times.json")
zip_code_travel_times = json.load(json_file)
def parse_time(t):

  try:
    t = str(t)
    if len(t) == 4:
      final = t[0] + t[1] + ":" + t[2] + t[3]
    else:
      final = t[0] + ":" + t[1] + t[2]
    d = datetime.strptime(final, "%H:%M")
    return d.strftime("%I:%M %p") 
  except:
    return str(t)

def get_travel_time(source, dest):

  try:
    return zip_code_travel_times[source][dest]
  except:

    try:
      url ='https://maps.googleapis.com/maps/api/distancematrix/json?'
      request_str = (url + 'origins=' + source +
                     '&destinations=' + dest +
                     '&key=' + api_key)
      r = requests.get(request_str)
      x = r.json()
      t = x["rows"][0]["elements"][0]["duration"]["value"]
      final = int(t/60)
      
      return final
    except:
      return 10

def get_travel_time1(source, dest):
  try:
    url ='https://maps.googleapis.com/maps/api/distancematrix/json?'
    request_str = (url + 'origins=' + source +
                   '&destinations=' + dest +
                   '&key=' + api_key)
    r = requests.get(request_str)
    x = r.json()
    t = x["rows"][0]["elements"][0]["duration"]["value"]
    final = int(t/60)
    
    return final
  except:
    return 10

def get_duration(source, dest):
  try:
    url ='https://maps.googleapis.com/maps/api/distancematrix/json?'
    request_str = (url + 'origins=' + source +
                   '&destinations=' + dest +
                   '&key=' + api_key)
    r = requests.get(request_str)
    x = r.json()
    t = x["rows"][0]["elements"][0]["duration"]["text"]
    
    
    return {"status": "success", "data": t}
  except:
    return {"status": "failed", "data": "N/A"}

def push_image_to_s3(k, path):
    obj = s3.Object('helio-patient-data',path + str(uuid.uuid1()) + ".JPG")
    obj.put(Body=k)


def upload_image_to_s3(filename, contents):
    obj = s3.Object('helio-patient-data', filename)

    result = obj.put(Body=contents)

    res = result.get('ResponseMetadata')

    if res.get('HTTPStatusCode') == 200:
        logger.info(f'File {filename} Uploaded Successfully')
        return True

    logger.warning(f'File {filename}Not Uploaded')
    return False


def get_s3_file_url(filename):
    try:
        s3_client = session.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': 'helio-patient-data',
                    'Key': filename},
            ExpiresIn=3600 * 24 * 7 - 1)
        return url
    except ClientError as e:
        logging.error(e)
        return None

def get_s3_file_url_intake_form(filename, contents):
    try:
        region = "us-east-2"
        obj = s3.Object('intake-form-saver', filename)
        result = obj.put(Body=contents)
        url = f"https://intake-form-saver.s3.{region}.amazonaws.com/{filename}"
        return url
    except ClientError as e:
        logging.error(e)
        return None

def push_label_to_s3(k, path):
    obj = s3.Object('helio-patient-data',path + str(uuid.uuid1()) + ".PDF")
    obj.put(Body=k)
    
def get_concat_h(im1, im2, im3, im4):
    dst = Image.new('RGB', (im1.width + im2.width + im3.width + im4.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    dst.paste(im3, (im1.width * 2, 0))
    dst.paste(im4, (im1.width * 3, 0))
    return dst

def upload_pdf(url, path):
  
  k = bytes(url, 'utf-8')
  
  k = base64.b64decode(url)
  img = convert_from_bytes(k)

  img[0] = img[0].crop((65, 200, 1570, 2000))
  img[1] = img[1].crop((65, 200, 1570, 2000))
  img[2] = img[2].crop((65, 200, 1570, 2000))
  img[3] = img[3].crop((65, 200, 1570, 2000))
  
  final = get_concat_h(img[0], img[1], img[2], img[3])
  buffered = BytesIO()
  final.save(buffered, format="JPEG")
  img_str = buffered.getvalue()

  obj = s3.Object('helio-patient-data',path + str(uuid.uuid1()) + ".JPG")
  obj.put(Body=img_str)

def get_random_str(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def calculate_age(birthDate): 
    today = date.today() 
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
  
    return age 

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def calculate_bmi(w, h):
  try:
    
    return (w / (h * h)) * 703
  except Exception as e:
    print(e)
    return -1


def get_percentile(sex, flag, age, param):
  try:
    if age > 20:
      age = 20
    age = age * 12
    if sex == 0:
      sex = "M"
    else:
      sex = "F"
    if flag == 0:
      param = param * 0.453592
      weight_z_score = calculator.wfa(param, age, sex)
      return norm.cdf(float(weight_z_score))
    elif flag == 1:
      param = param * 2.54
      height_z_score = calculator.lhfa(param, age, sex)
      return norm.cdf(float(height_z_score))
    else:
      bmi_z_score = calculator.bmifa(param, age, sex)
      return norm.cdf(float(bmi_z_score))
  except Exception as e:
    print(str(e))
    return -1

def parse_final_date(k):
    kk = k.split("/")
    x = int(kk[2]) * 10000 + int(kk[0]) * 100 + int(kk[1])
    return x

def get_data_from_s3(dir):
    try:
        files_in_s3 = [f.key.split(dir + "/")[1] for f in s3_bucket.objects.filter(Prefix=dir).all()]
        
        res = []
        for i in files_in_s3:
            if i != "":
                res.append(i)
        if res == []:
            ["nothing.pdf", BytesIO(bytes("", 'utf-8'))]
        else:
            obj = s3.Object('helio-patient-data', dir + "/" + res[0])
            obj_bytes =  obj.get()['Body'].read()

        # return [res[0], base64.b64encode(obj_bytes).decode()]
        return [res[0], BytesIO(obj_bytes)]
    except Exception as e:
        return ["nothing.pdf", BytesIO(bytes("", 'utf-8'))]

def write_error_to_db(e):
  connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)
  connection.commit()
  cursor = connection.cursor()
  cursor.execute("insert into errors (error) values (\"" + str(e) + "\")")
  connection.commit()

def field_validations_for_patient_enrollment(patient_data):
    try:
        patient_first_name, patient_last_name = patient_data.get("patient_name").split(' ')
        dob_date = patient_data.get("dob_date")
        dob_month = patient_data.get("dob_month")
        dob_year = patient_data.get("dob_year")
        phone = patient_data.get("phone")
        if dob_date == 0 and dob_month == 0 and dob_year == 0:
            dob = "01-01-2000"
        else:
            if len(str(dob_date)) != 2:
                dob_date = str(0) + str(dob_date)
            if len(str(dob_month)) != 2:
                dob_month = str(0) + str(dob_month)
        dob = f'{dob_month}-{dob_date}-{dob_year}'
        if phone is None:
            pass
        elif phone.startswith("+1"):
            phone = phone.replace('+1', '')
            phone = "(" + phone[:3] + ")-" + phone[3:6] + "-" + phone[6:]
        else:
            phone = "(" + phone[:3] + ")-" + phone[3:6] + "-" + phone[6:]
        zipcode = patient_data.get("zipcode")
        if not zipcode:
            zipcode = None
        elif len(str(zipcode)) == 4:
            zipcode = int(str("0"+zipcode))

        address = patient_data.get("address").split(',')
        if not address:
            address_line_one = address_line_two = city = state = None
        else:
            if len(address) == 5:
                address_line_one = address[0].strip()
                address_line_two = address[1].strip()
                city = address[-3].strip()
                state = address[-2].strip()
            elif len(address) == 4:
                address_line_one = address[0].strip()
                address_line_two = None
                city = address[-3].strip()
                state = address[-2].strip()
        data = {
                "patient_first_name": patient_first_name,
                "patient_last_name": patient_last_name,
                "dob": dob,
                "mobile_phone": phone,
                "zipcode": zipcode,
                "address_line_one": address_line_one,
                "address_line_two": address_line_two,
                "city": city,
                "state": state,
                "vendor_unique_transaction_id": generate_number()
                }
        return True, data
    except Exception as e:
        return False, str(e)

def generate_number():
    number = random.randint(1, 200000000)
    return number
