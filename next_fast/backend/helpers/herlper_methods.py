import base64
import os
import pathlib
import uuid
import logging
import fitz
from drchrono_sync_new import s3_client, s3_region, s3_patient_bucket

PARENT_DIRECTORY = pathlib.PurePath(pathlib.Path().parent.absolute()).parent
logger = logging.getLogger("fastapi")


def add_signature_to_pdf(sig_file, is_monthly, date, client_host):
    if is_monthly:
        form_path = pathlib.Path(PARENT_DIRECTORY) / "backend/pdfs/intake_form/4month.pdf"
    else:
        form_path = pathlib.Path(PARENT_DIRECTORY) / "backend/pdfs/intake_form/12month.pdf"
    doc = fitz.open(form_path)
    width = 200
    height = 50
    left = 190
    top = 367
    page = doc[2]
    page.wrap_contents()
    page.insert_image(fitz.Rect(left, top, left + width * 2, top + height), stream=sig_file)
    page.insert_text((324, 440), f"Date: {date}")
    page.insert_text((324, 460), f"IP: {client_host}")
    file_name = str(uuid.uuid4()) + ".pdf"
    doc.save(file_name)
    with open(file_name, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
    url = upload_file_to_s3({"file_content": encoded_string})
    os.remove(file_name)
    return url


def upload_file_to_s3(data, bucket_name=s3_patient_bucket, decode_file=True):
    url = ""
    try:
        if decode_file:
            body = base64.b64decode(data.get('file_content'))
        else:
            body = data.get('file_content')
        file_extension = data.get('extension', 'pdf') or 'pdf'
        key = str(uuid.uuid4()) + f".{file_extension}"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=body,
        )
        url = get_s3_url(key)
    except Exception as e:
        logger.exception("upload_file_to_s3 ==> " + str(e))
    return url


def get_s3_url(key):
    return f"https://s3.{s3_region}.amazonaws.com/{s3_patient_bucket}/{key}"
