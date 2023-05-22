import os
import logging
import boto3
from smtplib import SMTP
from botocore.client import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from twilio.rest import Client
from botocore.exceptions import ClientError
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, get_aws_sns_client, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

USERNAME_SMTP = "AKIAQXYVC547EKFMCXHF"
PASSWORD_SMTP = "BIxfrtJ/H4/rA7JEdYLcnHlVmuHo8V/GYifovCNkwBg9"

SMTP_HOST = "email-smtp.us-east-2.amazonaws.com"
SMTP_PORT = 587

s3_region = 'us-east-2'
s3_client = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    config=Config(
        signature_version='s3v4',
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
)

def get_log_level():
    level_env = os.getenv("FASTAPI_LOG_LEVEL", "INFO")
    if level_env.upper() == "DEBUG":
        return logging.DEBUG
    elif level_env.upper() == "WARN":
        return logging.WARNING
    elif level_env.upper() == "ERROR":
        return logging.ERROR
    elif level_env.upper() == "INFO":
        return logging.INFO
    else:
        return logging.INFO


def send_text_email(sender: str, recipient: str, subject: str, content: str):
    """Send Plain text email using SNMP"""
    try:
        msg = MIMEText(content, 'plain')
        msg['Subject'] = subject
        msg['From'] = sender

        conn = SMTP(SMTP_HOST, SMTP_PORT)
        conn.ehlo()
        conn.starttls()
        conn.ehlo()
        conn.login(USERNAME_SMTP, PASSWORD_SMTP)
        conn.sendmail(sender, recipient, msg.as_string())
        conn.close()
    except Exception as e:
        logging.exception(e)


def send_html_email(sender: str, recipient: str, subject: str, html: str):
    """Send HTML text email using SNMP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        conn = SMTP(SMTP_HOST, SMTP_PORT)
        conn.ehlo()
        conn.starttls()
        conn.ehlo()
        conn.login(USERNAME_SMTP, PASSWORD_SMTP)
        conn.sendmail(sender, recipient, msg.as_string())
        conn.close()
    except Exception as e:
        logging.exception(e)


def download_file(filename, url):
    pdf_path = f'pdfs/drchrono_documents/{filename}.pdf'
    try:
        logging.debug(f"downloading pdf {url}")
        response = requests.get(url)
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        f.close()
        return pdf_path
    except Exception as e:
        logging.exception(e)
    return None


def delete_file(file_path):
    if file_path is None:
        return
    try:
        logging.debug(f"Deleting downloaded pdf {file_path}")
        os.remove(file_path)
    except Exception as e:
        logging.exception(e)


def send_text_message_twilio(to_phone: str, message: str):
    """Send text notification via Twilio"""
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    from_phone = '+18454069635'
    if to_phone.startswith('+1'):
        pass
    elif to_phone.startswith('+'):
        pass
    else:
        to_phone = '+1' + to_phone

    logging.info(f"Sending notification to {to_phone}...")
    message = twilio_client.messages.create(
        body=message,
        from_=from_phone,
        to=to_phone
    )
    logging.debug(message.sid)


def send_text_message(to_phone: str, message: str):
    """Send text notification via AWS SNS"""
    if to_phone.startswith('+1'):
        pass
    elif to_phone.startswith('+'):
        pass
    else:
        to_phone = '+1' + to_phone
    aws_sns_client = get_aws_sns_client()
    res = aws_sns_client.publish(
        PhoneNumber=to_phone,
        Message=message
    )
    logging.debug(res)

def download_s3_file(file_to_download, bucket_name):
    try:
        s3_client = boto3.resource('s3')
        if bucket_name == "drchronodoc":
            s3_bucket = "drchronodoc"
        elif bucket_name == "patient-upload":
            s3_bucket = "patient-upload"
        return True, s3_client.Object(bucket_name=s3_bucket, key=file_to_download).get()['Body'].read()
    except ClientError as e:
        return False, str(e)

def check_file_in_s3(file):
    """param file: File to check if present in a bucket."""
    try:
        bucket = "drchronodoc"
        s3_client = boto3.client('s3')
        result = s3_client.list_objects_v2(Bucket=bucket, Prefix=file)
        if 'Contents' in result:
            return bucket
        else:
            bucket = "patient-upload"
            result = s3_client.list_objects_v2(Bucket=bucket, Prefix=file)
            return bucket
    except ClientError as e:
        logging.error(e)
        return None

def create_presigned_url(bucket_name, object_name, expiration=432000):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
