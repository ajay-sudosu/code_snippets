import datetime
import email.utils
import json
import logging
from retry import retry
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from pprint import pformat
from typing import Optional, List

import requests
from dateutil.parser import parse
from pydantic import BaseModel

import db_client
from api.klaviyo_api import klaviyo_track_profile, klaviyo_mdi_prescription_approved
from config import *
from curexa import curexa
from stripe_api import get_subscription, update_subscription
from utils import send_text_email, send_html_email
from database.crud import MDIMappingCrud, MDICaseMappingCrud
from sqlalchemy.orm import Session

logger = logging.getLogger("fastapi")
if is_prod is True:
    CLIENT_ID_ACCUTANE = 'ed0d6011-1005-43f8-989c-83e93cbeaa1c'
    CLIENT_SECRET_ACCUTANE = 'eOXsA45yiIn6CRIPigOEVzBhzDJs9zPIXR3AFctt'
    CLIENT_ID_WEIGHTLOSS = '8215aa84-5c9b-46d3-b361-5a73eb236868'
    CLIENT_SECRET_WEIGHTLOSS = 'XGrKnCvL4ZtkJ7I5sZyTbjjo7Nr6zn2V4SjW2a9y'
    CLIENT_ID = '07a1b833-1aa2-4938-a2af-4bac6dbe8c95'
    CLIENT_SECRET = '6SACBkwu7nzb75xAR6ixrWRevIXiBk90hcS7KVpM'
    CLIENT_ID_TESTOSTERONE = '6e0f2bc5-13d8-4c44-956f-233bfdb6ea46'
    CLIENT_SECRET_TESTOSTERONE = 'NoZ2uGdt9uo3EdssfTKRQ9IURn2pyAUMkQuouxai'
    CLIENT_ID_CANADA = 'd29ab6e8-a167-4bc2-b497-3dd4f23dd75b'
    CLIENT_SECRET_CANADA = 'wxRwOoTocTipK84K2gsKQkTmxWwNQhd112lW9R3a'
    CLIENT_ID_AGING = '019881fe-124a-4ed4-9e14-3c402d201565'
    CLIENT_SECRET_AGING = 'I9jr60oNLuuCDTRTR1s4fcQK2KfD7jRXZeb3xxpF'
    CLIENT_ID_DIAGNOSTICS = '97c66751-4fac-4ced-acf8-5615f8c8b044'
    CLIENT_SECRET_DIAGNOSTICS = 'SwrpJ6GxKYBK6ghjGAI8Fsfl6d7SDHTy7tUYt8Bg'
else:
    CLIENT_ID_ACCUTANE = 'da961287-a09a-4581-b336-4770d2b82de3'
    CLIENT_SECRET_ACCUTANE = '30xmGga7yQGzllEN9VqTHkZBQ5kwfcXlayfZIkHx'
    CLIENT_ID_WEIGHTLOSS = '8215aa84-5c9b-46d3-b361-5a73eb236868'
    CLIENT_SECRET_WEIGHTLOSS = 'XGrKnCvL4ZtkJ7I5sZyTbjjo7Nr6zn2V4SjW2a9y'
    CLIENT_ID = '5fa66165-d455-4033-bc34-5d5dc63ac432'
    CLIENT_SECRET = 'gLCBenXvzDnw3yPt5zFsSKSFrU5P2rkdDPUaGVZT'
    CLIENT_ID_TESTOSTERONE = '6e0f2bc5-13d8-4c44-956f-233bfdb6ea46'
    CLIENT_SECRET_TESTOSTERONE = 'NoZ2uGdt9uo3EdssfTKRQ9IURn2pyAUMkQuouxai'
    CLIENT_ID_CANADA = ''
    CLIENT_SECRET_CANADA = ''
    CLIENT_ID_AGING = ''
    CLIENT_SECRET_AGING = ''
    CLIENT_ID_DIAGNOSTICS = '97c66751-4fac-4ced-acf8-5615f8c8b044'
    CLIENT_SECRET_DIAGNOSTICS = 'SwrpJ6GxKYBK6ghjGAI8Fsfl6d7SDHTy7tUYt8Bg'

WEBHOOK_SECRET = '__webhook__123@#'
WEBHOOK_TOKEN = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzMDEzOTQ0YS00OWNlLTRiYTktOGM2NC03YmUzYjFmYTQ2MDkiLCJhdWQiOiI2NmZvdnBqNHZjcDk0ODhsYjlvN24zcnY1OCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImE3MWMzYjQ2LWMyZDktNDNkNi05M2E0LTdjMjU3NWI3NGQ2YSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjMxNjUzMDYzLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0yLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMl92cENSZkl2WEQiLCJjb2duaXRvOnVzZXJuYW1lIjoiMzAxMzk0NGEtNDljZS00YmE5LThjNjQtN2JlM2IxZmE0NjA5IiwiZXhwIjoxNjMxNzM5NDYzLCJpYXQiOjE2MzE2NTMwNjMsImVtYWlsIjoiZnJhbmtAam9pbm5leHRtZWQuY29tIn0.UezojBQdq2o-5ib43J3L4ZO1LFQwAQvHa_zv2TtKXl-WVQGbr7RB2_G3iJa0pPkPQOPMp1fBVspILqEk28KlbmXqhMDmMmY97V8DD18Gmi8qjxSjOCt3GS976X8Z2CP7uLn15706PBpG76GCmq8lkaIrXiIYBT-UzcAFTcsDMUAsRK2M1R1Z14IDB-oTg6y1hBwpjLAvQ1K8HFU1NLG-iifqWj9-fB4NtouJMtWBieF1j6UWTwmT36zVpJAqCR8eLRc3JBjUYM-SzVHNec7_KcZNXWAZsr82p8QdpMARQi-1RcrNmnYAFFRniqq0w9ZJr0BxGE2Oy26Lu607OqR7YQ'
WEBHOOK_TOKEN_ACCUTANE = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6IjBjN2ZmZTkxLTdlM2QtNDUzNC05ZTg4LTMxM2M3ODdmY2FhNSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY0OTgzNDMyLCJwaG9uZV9udW1iZXIiOiIrOTE4ODI2MDA2NTA4IiwiZXhwIjoxNjY1MDY5ODMyLCJpYXQiOjE2NjQ5ODM0MzIsImVtYWlsIjoidXJzdGVhbHRoQGdtYWlsLmNvbSJ9.Jydl2rGWqIO15uxhDMMpJ0dvrYHcJdK7fZXAJZyvykepbFYfLb8qYiqrGkDBfYBYkRj-soyZ75ox6jRb0KeRUFcXQfwFHQEbTk5U0SXUbiTGyPHvtORI5nvxpAus8fiz1X00bT5sIZ7P5iK_crz8YGXIFvYSNfVytXRbk-kyi3_rxMLB_ItnLOyI5xcZer2uAmq4j4bG-94orKLnI5GxFqH6CE_6LwbvXWZebDZwzyw-FduD5EsXRdatLZ0VPpBZ3jIGInQrNx1_Vw82MVi20_pgjPayOZLkqNfPOIf2rSw3O-JT4bxRgds_zY-qFYgZtOVOy2STYUyAkOM3071VMw'
WEBHOOK_TOKEN_WEIGHTLOSS = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6ImZiYjhmOTkyLTcwYmYtNDU0MS1hNGQ3LTMxOTk2NWJiNWNjMCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY0OTgzNzE4LCJwaG9uZV9udW1iZXIiOiIrOTE4ODI2MDA2NTA4IiwiZXhwIjoxNjY1MDcwMTE4LCJpYXQiOjE2NjQ5ODM3MTgsImVtYWlsIjoidXJzdGVhbHRoQGdtYWlsLmNvbSJ9.RXMXFdLT-dy3NU1v2lI3Gd4pYgAbUzQxiWKzr4j7lkwQRXdXR3WIF_JtGPUXLqsO-HqrowWT_VfXYETfcfBkewfXx9sl3Ff9IML_PxNz4yf8qbpmZXBEY1wNIPyVhBgD2NUoCPhnncWsLB4wcCWU99shjPxmapdBsncUeDz1RQAREE1ZTTrdnycq7sTfcGrfmKMlsXljDsJ_Da_VK3CkUWFuUlh9vV4X7GMerZb_nQkGpoR-McXTt72oW4rBnAb-zSJn2-HpWGuHj-IicG5Ckx_PrBXvlr7_cjO4zrSz8En1uFTT75l7B8C9LjgbgufbqXsUPU7w-i1vfhhdb9mSww'
WEBHOOK_TOKEN_TESTOSTERONE = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6IjMxMjQwMzZiLTVmMWQtNDdkOS1iZTg2LWIxZWYwNGQ5OTIxNiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY1MzM2MzI1LCJwaG9uZV9udW1iZXIiOiIrOTE4ODI2MDA2NTA4IiwiZXhwIjoxNjY1NDIyNzI1LCJpYXQiOjE2NjUzMzYzMjUsImVtYWlsIjoidGFyaXF1ZUBqb2lubmV4dG1lZC5jb20ifQ.OL82kcB--8NskugjE-rLmDq5wJKrqXj2MCwn-Bja3AG3PMPfTUvB2t1Z9CcdZHEUDN6EZ2BSNiosTUX_q_kitIp5u8BjhqDFsmFgM3CWhaHw4B5dPBsZuUFElgfdo4xLvmWM3HekqlWtY0sEbt3v4AIP6UzQcfZ4OsPRPLCUGUzn02KHwBK8eoQ9uExwLc7o9fdrXczsI_mju4WCFA4STfiI4xQNE_uPlLCmV-a7aDxtLBB0Yy8Rl54PiMRemKspTWHzQqDnpX1VgaLK1IYarAXqknQMMWLRYkAZsXkpD9uQZYaSnF6mlhmeMqnXu7jZEXYVve9sDJjVZt9QxW-2jw'
WEBHOOK_TOKEN_CANADA = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6Ijg4MmYzMWZmLTgxNWEtNDQ4Ni05OGJjLTAyOGQ2ZGZhYzI4YyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY2NDU4NDExLCJwaG9uZV9udW1iZXIiOiIrOTE4ODI2MDA2NTA4IiwiZXhwIjoxNjY2NTQ0ODExLCJpYXQiOjE2NjY0NTg0MTEsImVtYWlsIjoidGFyaXF1ZUBqb2lubmV4dG1lZC5jb20ifQ.IAC9cjrmLmYocK8OdRG0EccHc_9Na-kOgQS_kalgXKez3gIKVfcQtmfcnrtKOuh5FxQNOUyYbSBtxgp5b7cN0nQ7E7TL-S5CSAEDW2wGWn3KiVEXpACr8o7xMwILEc91clLi31o93UNkLRgKRJETneyo7l6vznw-69spZSLSW_UnWQtzDCIRr5ypjRsTrwstIaDLcqzr-Yz3Jg767fYJCQOdMaIxBXSa7_u4yka7IZTT-M5RVtUFVNPtqTXt2Tb3EWOL6PObHNX2KRTbLiJ86gc4n6YWHjpjeruZIf9aNmd-xuLX-p8iLAsLRJ5ZVTWbMEdc6IjL8O6_FmnAJxUOdQ'
WEBHOOK_TOKEN_AGING = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6ImI3YmVlNzNlLTVlMWUtNGU2My04NGI3LTIyYmM1NWI1YTNjZiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY2NDU4NTA1LCJwaG9uZV9udW1iZXIiOiIrOTE4ODI2MDA2NTA4IiwiZXhwIjoxNjY2NTQ0OTA1LCJpYXQiOjE2NjY0NTg1MDUsImVtYWlsIjoidGFyaXF1ZUBqb2lubmV4dG1lZC5jb20ifQ.a5uuT9ERz8v2gIytJd4Yi-xTKXeWX5NNkFtO_4F_18BmdLgJtH5FWkIpck7L8KPFVtHVilu5nzKrUF9vkf4IfBDFXbUDiu6HGIVhmJL2V__mjeMi6P7-QdIyNX4qIIozsuLTP4FhjT-kGEwZK3HkwrFwaO0Grq9N_LY5be6TTQgGu9lp7s0M2cLeto8x6VlSZ4zAmL9YuGXsv_RTzCMoTzeS-DCdajTuHxobsrJA-sFcb_qiboHA8m-9KZ4qEb4kQ5-E78ztFc9BHNWCcbW9_KAUI3jMeh6rPPDQNQrScjSrgdLLTMjV3JQ0mkuYYz37GsZ98QSGn221ffuhW692kw'
WEBHOOK_TOKEN_DIAGNOSTICS = 'Bearer eyJraWQiOiJPcFVSUHJRTnBLWmpGdCtaS3Ryb2I5Qm0xQVJTR25kUHBmWFk4WGhWcVwvWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIwMGFhYTk2Mi03OTRjLTQ4YWYtOGNkZC1lNmMzNWYxMjdjOWUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfdnBDUmZJdlhEIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjb2duaXRvOnVzZXJuYW1lIjoiMDBhYWE5NjItNzk0Yy00OGFmLThjZGQtZTZjMzVmMTI3YzllIiwiYXVkIjoiNjZmb3ZwajR2Y3A5NDg4bGI5bzduM3J2NTgiLCJldmVudF9pZCI6ImIwNjIyZmYzLTFhYWItNDdmYi1hNmE1LTIwYjY1MDI0NGY1ZSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjY4ODUxNzM4LCJuYW1lIjoiVGFyaXF1ZSBBbndlciIsInBob25lX251bWJlciI6Iis5MTg4MjYwMDY1MDgiLCJleHAiOjE2Njg5MzgxMzgsImlhdCI6MTY2ODg1MTczOCwiZW1haWwiOiJ4ZW51bTR1QGdtYWlsLmNvbSJ9.PuqY6BHNS_0YsqyDeSNwxX6ilSW6TrYho-a_1oByvJrfTlt3zg6rA3El1MZGSx170YGSJ48Ff4Oc9W_vdljAxbt7C0NTEhpcZi1F7RqZ7MXoGQE2RjvMaR1gZALfUJUpudKsRwC0V5yeuO9_jX3vYwBnOL9q6_2_FRVxZjM7GsFrWLlvQljrasrgrUM3wbCTKWDpWxRGYBysonam4aJKVgY_8-Npg5-vlv6U2JRgnXQ2sfsX1MSL506H4EganwqerrDupMuS67D-CGdYWa0WivMa4nFBtoHYLkpfkOFzkn5Xzagal-xamMl6TkNzn-sxgeIvQWNMOHoooUJmyoPbaA'

SENDER = 'team@joinnextmed.com'
SENDERNAME = 'Next Medical'

USERNAME_SMTP = "AKIAQXYVC547EKFMCXHF"
PASSWORD_SMTP = "BIxfrtJ/H4/rA7JEdYLcnHlVmuHo8V/GYifovCNkwBg9"

HOST = "email-smtp.us-east-2.amazonaws.com"
PORT = 587


class MDintegrationsAddress(BaseModel):
    address: str
    zip_code: str
    city_id: Optional[str]
    city_name: Optional[str]
    state_name: Optional[str]


class MDintegrationsPatient(BaseModel):
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    gender: int
    phone_number: str
    phone_type: int
    address: MDintegrationsAddress
    driver_license_id: Optional[str]
    metadata: Optional[str]
    weight: Optional[float]
    height: Optional[int]
    allergies: Optional[str]
    pregnancy: Optional[bool]
    current_medications: Optional[str]


class MDICreateCase(BaseModel):
    hold_status: Optional[bool]
    patient_id: str
    metadata: Optional[str]
    clinician_id: Optional[str]
    case_prescriptions: Optional[List]
    case_files: Optional[List]
    case_questions: Optional[List]
    case_services: Optional[List]
    is_chargeable: Optional[bool]
    subscription_id: Optional[str]
    test_type: Optional[str]


class MDICreateCaseMedicine(BaseModel):
    hold_status: Optional[bool]
    patient_id: str
    metadata: Optional[str]
    clinician_id: Optional[str]
    medicine: str
    case_files: Optional[List]
    case_questions: Optional[List]
    case_services: Optional[List]
    is_chargeable: Optional[bool]
    subscription_id: Optional[str]
    test_type: Optional[str]


class MDintegrationsCase(BaseModel):
    patient_id: str
    metadata: Optional[str]
    clinician_id: Optional[str]
    case_prescriptions: Optional[List]
    case_files: Optional[List]
    case_questions: Optional[List]


class MDintegrationsPatientPharmacy(BaseModel):
    patient_id: str
    pharmacy_id: int
    set_as_primary: Optional[bool]


class MDICreateHerpesCase(BaseModel):
    mrn: str
    subscriptionId: Optional[str] = None
    subscriptionType: Optional[str] = None


class MDICreatePrescriptionsCase(BaseModel):
    mrn: str
    subscriptionId: Optional[str] = None
    medicineList: Optional[list]


class MDICasePrescription(BaseModel):
    case_id: str


class MDICasePrescriptionUpdate(BaseModel):
    case_id: str
    prescriptions: list


class MDIPatientId(BaseModel):
    patient_id: str


class MDISearchPharmacy(BaseModel):
    city: Optional[str]
    state: Optional[str]
    zip: Optional[int]
    address: Optional[str]
    ncpdpID: Optional[int]
    name: Optional[str]


class MDintegrationsAPI:
    token_filename = 'mdi_token.json'
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET

    def __init__(self, prod=False):
        self.token = None
        self.prescriptions = []
        self.case = None
        if prod:
            self.base_url = 'https://api.mdintegrations.com'
        else:
            self.base_url = 'https://api.mdintegrations.xyz'

    def refresh_access_token(self):
        """Fetch new access token from mdi api"""
        uri = '/v1/partner/auth/token'
        logger.debug(f"Refreshing MDI token for {self.client_id}")
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "*"
        }
        response = requests.post(self.base_url + uri, json=payload)
        if response.status_code == requests.codes.ok:
            self.token = response.json()
            token_file = Path(self.token_filename)
            with open(token_file, "w") as outfile:
                mdi_token_info = {"token": self.token, "datetime": str(datetime.datetime.now())}
                json.dump(mdi_token_info, outfile)
        else:
            logger.debug(response.status_code)

    def fetch_access_token(self):
        """Fetch new access token"""
        token_file = Path(self.token_filename)
        token_file.touch(exist_ok=True)
        with open(token_file, 'r') as openfile:
            try:
                mdi_token_info = json.load(openfile)
            except json.decoder.JSONDecodeError:
                mdi_token_info = {}
            if mdi_token_info and \
                mdi_token_info.get('token') and \
                mdi_token_info.get('token') not in ['', None] and \
                mdi_token_info.get('datetime'):
                time_difference_seconds = (
                        datetime.datetime.now() - parse(mdi_token_info.get('datetime'))
                ).total_seconds()
                if time_difference_seconds <= 10800:  # 3 hours
                    self.token = mdi_token_info['token']
                    return
        self.refresh_access_token()

    @retry(PermissionError, delay=0, tries=3)
    def _post_request_(self, uri, params=None, json=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri
        self.fetch_access_token()
        access_token = self.token.get('access_token')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if json is None:
            res = requests.post(url, headers=headers, params=params)
        else:
            res = requests.post(url, headers=headers, params=params, json=json)
        if res.status_code == 200:
            pass
        elif res.status_code == 401:
            self.refresh_access_token()
            logger.error(res.status_code)
            raise PermissionError('Unauthorized Access')
        else:
            logger.error(f"{uri}: {res.status_code} {headers} {params}, {json}")
        return res.json()

    @retry(PermissionError, delay=0, tries=3)
    def _get_request_(self, uri, params=None):
        """
                Send a requests.get request
                :param uri: Endpoint URI
                :param params: URL Parameters
                :param json: body to be sent with request
                :return: json of response
        """
        url = self.base_url + uri
        self.fetch_access_token()
        access_token = self.token.get('access_token')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            pass
        elif response.status_code == 401:
            self.refresh_access_token()
            logger.error(response.status_code)
            raise PermissionError('Unauthorized Access')
        else:
            logger.error(f"{uri}: {response.status_code} {headers} {params}")
        return response.json()

    def _delete_request_(self, uri, params=None, json=None):
        """
                Send a requests.delete request
                :param uri: Endpoint URI
                :param params: URL Parameters
                :param json: body to be sent with request
                :return: json of response
        """
        url = self.base_url + uri
        self.fetch_access_token()
        access_token = self.token.get('access_token')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.delete(url, headers=headers, params=params, json=json)
        if response.status_code == 200:
            pass
        elif response.status_code == 401:
            self.refresh_access_token()
            logger.error(response.status_code)
            raise PermissionError('Unauthorized Access')
        else:
            logger.error(f"{uri}: {response.status_code} {headers} {params}, {json}")
        return response.json()

    def _patch_request_(self, uri, params=None, json=None):
        """
        Send a requests.patch request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri
        self.fetch_access_token()
        access_token = self.token.get('access_token')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if json is None:
            res = requests.patch(url, headers=headers, params=params)
        else:
            res = requests.patch(url, headers=headers, params=params, json=json)
        if res.status_code == 200:
            pass
        elif res.status_code == 401:
            self.refresh_access_token()
            logger.error(res.status_code)
            raise PermissionError('Unauthorized Access')
        else:
            logger.error(f"{uri}: {res.status_code} {headers} {params}, {json}")
        return res.json()

    def create_patient(self, data):
        """Creates a new patient record both on MD Integrations and DoseSpot."""
        uri = '/v1/partner/patients'
        if 'test_type' in data:
            del data["test_type"]
        # remove None values
        new_data = {k: v for k, v in data.items() if v}
        response = self._post_request_(uri, json=new_data)

        # if creation failed return exiting patient details
        if 'message' in response and response.get('message') == 'ERROR_PATIENT_EMAIL_ALREADY_TAKEN':
            data1 = {
                "search": data.get("email")
            }
            patient_list = self.search_patient(data1)
            if len(patient_list) != 0:
                logger.info(f"Patient already exists with email={email} returning same.")
                return patient_list[0]
        return response

    def update_patient(self, patient_id, data):
        """Update a patient record both on MD Integrations and DoseSpot."""

        uri = f'/v1/partner/patients/{patient_id}'

        return self._patch_request_(uri, json=data)

    def get_patient(self, patient_id):
        """Return details for a given patient ID."""
        uri = f"/v1/partner/patients/{patient_id}"

        return self._get_request_(uri)

    def get_patient_pharmacies(self, patient_id):
        """Retrieves a detailed list of preferred pharmacies in the patient’s record. This API endpoint forwards the
        request to DoseSpot API in order to retrieve this information."""
        uri = f"/v1/partner/patients/{patient_id}/pharmacies"

        return self._get_request_(uri)

    def search_patient(self, data):
        """This route returns a list of Patients based on the "search" string parameter passed.
        Should be either the patient's full name, last name or e-mail.
        """
        uri = '/v1/partner/patients/search'

        return self._post_request_(uri, json=data)

    def create_file(self, file):
        """Upload a single file to MD Integrations using multipart/form-data."""
        uri = '/v1/partner/files'
        url = self.base_url + uri
        self.fetch_access_token()
        access_token = self.token.get('access_token')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content': 'multipart/form-data;',
            'Accept': 'application/json',
        }
        files = {'file': file}
        payload = {
            'name': "results",
        }
        r = requests.post(url, files=files, headers=headers, data=payload)
        return r.json()

    def mdi_create_file(self, filepath: str):
        """create file on mdi"""
        if not os.path.exists(filepath):
            logger.warning(f"{filepath} doesn't exist.")
            return None
        logger.debug(f"Creating file on mdintegrations: {filepath}")
        with open(filepath, 'rb') as f:
            response = self.create_file(f)
            logger.debug(response)
            file_id = response.get('file_id')
            return file_id

    def create_case(self, data):
        """Create a new case for a given patient."""
        uri = '/v1/partner/cases'
        if 'test_type' in data:
            del data['test_type']

        # MDI case.question.answer must not be '' #1385
        for question_dict in data.get('case_questions', []):
            answer = question_dict.get('answer')
            if not answer:
                question_dict['answer'] = 'NA'
            # MDI case.question must be <255 #NXTMD-593
            question_text = question_dict.get('question')
            if len(question_text) > 254:
                question_dict['question'] = question_text[:254]
                question_dict['description'] = question_text[254:]

        # NXTMD-385 fix
        if 'case_files' in data:
            # remove all None from list
            data['case_files'] = [i for i in data['case_files'] if i is not None]

            # delete if empty list
            if not len(data['case_files']):
                del data['case_files']

        return self._post_request_(uri, json=data)

    def create_case_to_support(self, case_id, data):
        """Add case to the support"""
        uri = f'/v1/partner/cases/{case_id}/support'

        return self._post_request_(uri, json=data)

    def get_case(self, case_id):
        """Return details for a given case ID."""
        uri = f"/v1/partner/cases/{case_id}"

        return self._get_request_(uri)

    def get_case_questions(self, case_id):
        """Return all questions for a given case ID."""
        uri = f"/v1/partner/cases/{case_id}/questions"

        return self._get_request_(uri)

    def update_case_questions(self, case_id: str, questions: list):
        """Update cases questions for case ID."""
        uri = f"/v1/partner/cases/{case_id}/questions"

        return self._patch_request_(uri, json=questions)

    def add_file_to_case(self, case_id, file_id):
        """Attach a file to a case."""
        uri = f"/v1/partner/cases/{case_id}/files/{file_id}"

        return self._post_request_(uri, json={})

    def get_case_files(self, case_id):
        """Returns a list of all attached files to the case."""
        uri = f"/v1/partner/cases/{case_id}/files"

        return self._get_request_(uri)

    def get_patient_cases(self, patient_id):
        """This endpoint returns all cases related to the patient passed on the request."""
        uri = f"/v1/partner/patients/{patient_id}/cases"
        return self._get_request_(uri)

    def get_pharmacy(self, pharmacy_id):
        """Get DoseSpot pharmacy details from a given pharmacy ID.
        This API endpoint forwards the request to DoseSpot in order to retrieve the pharmacy details."""
        uri = f"/v1/partner/pharmacies/{pharmacy_id}"

        return self._get_request_(uri)

    def get_pharmacies(self, params=None):
        """Search DoseSpot pharmacies according to a given query parameter. At least one query parameter is required.
        If no query parameter is provided, an error will be thrown.
        This API endpoint forwards the request to DoseSpot in order to search for pharmacies."""
        uri = f"/v1/partner/pharmacies"

        return self._get_request_(uri, params=params)

    def get_prescription(self, case_id):
        """Search DoseSpot pharmacies according to a given query parameter. At least one query parameter is required.
        If no query parameter is provided, an error will be thrown.
        This API endpoint forwards the request to DoseSpot in order to search for pharmacies."""
        logger.debug(case_id)
        uri = f"/v1/partner/cases/{case_id}/prescriptions"

        return self._get_request_(uri)

    def update_case_prescriptions(self, case_id, data):
        """Update cases prescriptions.
        Receives an array of Prescriptions.
        Important: a prescription object must always contain exactly one drug type ID
        from the following: [partner_medication_id, partner_compound_id]"""
        uri = f"/v1/partner/cases/{case_id}/prescriptions"

        return self._patch_request_(uri, json=data)

    def add_pharmacy_to_patient(self, patient_id, pharmacy_id, set_as_primary=False):
        """Adds a pharmacy to a patient’s preferred pharmacies list.
        This API endpoint forwards the request to DoseSpot API in order to add patient's pharmacies."""
        uri = f'/v1/partner/patients/{patient_id}/pharmacies/{pharmacy_id}'

        data = {
            "set_as_primary": set_as_primary
        }

        return self._post_request_(uri, json=data)

    def add_case_to_support(self, case_id):
        """Adds a pharmacy to a patient’s preferred pharmacies list.
        This API endpoint forwards the request to DoseSpot API in order to add patient's pharmacies."""
        uri = f'/v1/partner/cases/{case_id}/support'

        data = {
            "reason": "Waiting for patient insurance approval and weight loss medication preferences"
        }

        return self._post_request_(uri, json=data)

    def get_all_medication(self):
        """Get all registered medications on Admin Panel related to the logged in partner."""
        uri = f"/v1/partner/medications"

        return self._get_request_(uri)

    def search_compounds(self, name=None):
        """Search compounds belonging to the logged partner.
        In case a search term is not provided, all the available compounds are returned."""
        uri = f"/v1/partner/compounds/search"

        param = {
            'name': name
        }

        return self._get_request_(uri, params=param)

    def list_services(self):
        """"""
        uri = f"/v1/partner/services"

        return self._get_request_(uri)


class MDintegrationsChat(MDintegrationsAPI):
    """class providing interface for mdintegrations' Case Messages"""

    def get_messages(self, case_id, channel):
        """Return all the messages for a given case according to the specified channel."""
        uri = f"/v1/partner/cases/{case_id}/messages"

        param = {
            "channel": channel
        }

        return self._get_request_(uri, params=param)

    def get_pharmacies(self, pharmacy_name):
        """Return all the pharmacies for a given case according to the specified channel."""
        uri = f"/v1/partner/pharmacies?zip=" + pharmacy_name

        return self._get_request_(uri)

    def get_pharmacies1(self, pharmacy_name, name):
        """Return all the pharmacies for a given case according to the specified channel."""
        uri = f"/v1/partner/pharmacies?zip=" + pharmacy_name + "&name=" + name

        return self._get_request_(uri)

    def create_messages(self, case_id, data):
        """Create a new message for a given case."""
        uri = f"/v1/partner/cases/{case_id}/messages"

        return self._post_request_(uri, json=data)

    def set_message_as_read(self, case_id, case_message_id):
        """Set a given message as read. The message is set as read for the
        current date and time when the request is sent."""
        uri = f"/v1/partner/cases/{case_id}/messages/{case_message_id}/read"

        return self._post_request_(uri, json={})

    def detach_message_file(self, case_id, case_message_id, file_id):
        """Detach a given file ID from a given message.
        The given file won't be deleted, only the association between
        the message and the file will be removed."""
        uri = f"/v1/partner/cases/{case_id}/messages/{case_message_id}/files/{file_id}"

        return self._delete_request_(uri, json={})

    def update_message(self, case_id, case_message_id, data):
        """Updates the message for a given case."""
        uri = f"/v1/partner/cases/{case_id}/messages/{case_message_id}"

        return self._patch_request_(uri, json=data)

    def _send_feedback_email_(self, case_id):
        try:
            # fetch case details
            case = self.get_case(case_id)

            patient_email = case.get('patient').get('email')
            patient_name = case.get('patient').get('first_name')

            subject = 'Feedback'
            content = get_html(message_type=1,
                               name=patient_name,
                               date='', time='', mrn='', address=''
                               )

            logger.info(f"Sending feedback email to {patient_email} for case_id={case_id}")
            send_html_email(sender=SENDER, recipient=patient_email, subject=subject, html=content)
        except Exception as e:
            logger.exception(e)

    def _update_stripe_subscription_(self, subscription_id, curexa_order):
        """Update stripe subscription"""
        logger.debug(f"Started")
        try:
            if subscription_id is None:
                logger.info(f"Not Updating stripe for {subscription_id}")
                return
            subscription = get_subscription(subscription_id)
            refills_ordered = subscription.get("metadata", {}).get("refills_ordered", 0)
            logger.info(f"Updating stripe {subscription_id}...")
            metadata = {
                "order": curexa_order,
                "refills_ordered": refills_ordered + 1
            }
            update_subscription(subscription_id, metadata=metadata)

        except Exception as e:
            logger.exception(e)

    def send_curexa_order(self, case_id, subscription_id=None):
        """Send curexa order"""
        logger.info(f"Sending order to curexa for {case_id}")
        try:
            # fetch prescription
            # prescriptions = self.get_prescription(case_id)
            if len(self.prescriptions) == 0:
                logger.warning(f"No prescription found for case_id: {case_id}")
                return None
            prescription = self.prescriptions[0]

            # fetch case details
            # case = self.get_case(case_id)
            patient = self.case.get('patient')

            if subscription_id is None:
                subscription_id = self.case.get('metadata')

            if prescription['medication'] is not None:
                rx_item = {
                    "rx_id": prescription['medication']['dosespot_medication_id'],
                    "medication_name": prescription['medication']['generic_product_name'],
                    "quantity_dispensed": prescription['quantity'],
                    "days_supply": prescription['days_supply'],
                    "medication_sig": prescription['directions'],
                    # 'medication_sig': 'Test prescription, please disregard.',
                    "non_child_resistant_acknowledgment": False
                }
                medication_name = prescription['medication']['display_name']
            else:
                rx_item = {
                    "rx_id": prescription['dosespot_prescription_id'],
                    "medication_name": prescription['partner_compound']['title'],
                    "quantity_dispensed": prescription['quantity'],
                    "days_supply": prescription['days_supply'],
                    "medication_sig": prescription['directions'],
                    # 'medication_sig': 'Test prescription, please disregard.',
                    "non_child_resistant_acknowledgment": False
                }
                medication_name = prescription['partner_compound']['title']

            first_name = patient['first_name']
            last_name = patient.get('last_name', "")
            order_id = f"{prescription['dosespot_prescription_id']}"
            curexa_order = {
                "order_id": order_id,
                "patient_id": patient['email'],
                "patient_first_name": first_name,
                "patient_last_name": last_name,
                "patient_dob": patient['date_of_birth'].replace('-', ""),
                "patient_gender": patient.get('gender_label', "male").lower(),
                "address_to_name": f"{first_name} {last_name}",
                "address_to_city": patient['address']['city_name'],
                "address_to_state": patient['address']['state']['abbreviation'],
                "address_to_street1": patient['address']['address'],
                "address_to_street2": patient['address']['address2'],
                "address_to_zip": patient['address']['zip_code'],
                "address_to_country": "US",
                "address_to_phone": patient['phone_number'].replace('-', ''),
                "patient_known_allergies": patient['allergies'],
                "patient_other_medications": patient['current_medications'],
                "carrier": "USPS",
                "rx_items": [
                    rx_item
                ]
            }
            # trigger klaviyo
            klaviyo_track_profile(
                event="ordered product",
                email=patient['email'],
                item_name=medication_name,
                item_type="Curexa",
                item_value=96.0,
                patient_name=f"{first_name} {last_name}",
                phone_number=patient['phone_number'].replace('-', '')
            )

            for k, v in curexa_order.items():
                if v is None or v == 'None':
                    curexa_order[k] = ""
            logger.info(curexa_order)
            res = curexa.create_order(curexa_order)
            logger.debug(res)
            res = curexa.order_status(order_id=order_id)
            logger.debug(res)
            if 'order_id' in res and res['order_id'] == order_id:
                logger.warning(f"Sent order to curexa for {case_id} Successfully.")
                db = db_client.DBClient()
                order_id = res.get('order_id')
                email = patient.get('email')
                logger.info(f"Insert into curexa_orders: order_id: {order_id} for {email}")
                db.insert_curexa_order(email, order_id)
                self._update_stripe_subscription_(subscription_id, curexa_order)
                return curexa_order
            else:
                logger.warning(f"Sending order to curexa for {case_id} Failed.")
                return None
        except Exception as e:
            logger.exception(e)
        return None

    def send_klaviyo_prescription_approved(self, case_id):
        """"""
        try:
            # fetch prescription
            self.prescriptions = self.get_prescription(case_id)
            if len(self.prescriptions) == 0:
                logger.warning(f"No prescription found for case_id: {case_id}")
                return None
            # fetch case details
            self.case = self.get_case(case_id)
            patient = self.case.get('patient')
            patient_name = f"{patient['first_name']} {patient.get('last_name', '')}"
            prescription = self.prescriptions[0]
            if prescription['medication'] is not None:
                display_name = prescription['medication']['display_name']
            else:
                display_name = prescription['partner_compound']['title']

            pharmacy = self.get_pharmacy(prescription['pharmacy_id'])
            klaviyo_mdi_prescription_approved(patient['email'], patient_name, display_name,
                                              pharmacy_name=pharmacy.get("name"))
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def curexa_order_check(case_id):
        """Check if order to be sent to curexa based on is_home_charge
        return True if to be sent else False
        """
        try:
            client = db_client.DBClient()
            visits = client.get_visits_by_case_id(case_id)
            # check if is_home_charge is 1
            for visit in visits:
                if visit.get('is_home_charge') == 1:
                    logger.debug(visit)
                    return True
        except Exception as e:
            logger.exception("curexa_order_check => " + str(e))
        return False

    def handle_webhook(self, data, test_type="normal"):
        """Handle webhook payload"""

        event_type = data.get('event_type')
        case_id = data.get('case_id')
        client = db_client.DBClient()
        logger.debug(f"test_type: {test_type}, event_type: {event_type}, case_id: {case_id}")
        if event_type is None:
            raise Exception(data)

        if 'case_completed' == event_type:
            self.send_klaviyo_prescription_approved(case_id)
            case_questions = self.get_case_questions(case_id)
            for que in case_questions:
                if que.get('answer') == 'REVIEW RESULTS':
                    self._send_feedback_email_(case_id)
                # order medication for herpes+ & requested
                if que.get('question') == 'MEDICATION' and que.get('answer') == 'MEDICINE REQUESTED':
                    self.send_curexa_order(case_id)
                    return
                # dont order medication for herpes+ & not requested
                elif que.get('question') == 'MEDICATION' and que.get('answer') != 'MEDICINE REQUESTED':
                    return
            # order medication for all rest if prescription is present
            if self.curexa_order_check(case_id):
                self.send_curexa_order(case_id)
        elif 'case_processing' == event_type:
            pass
        elif 'case_waiting' == event_type:
            pass
        elif 'case_cancelled' == event_type:
            pass
        elif 'case_transferred_to_support' == event_type:
            recipient = 'team@joinnextmed.com'
            subject = 'Action Needed'
            content = f"""
            Hi Team,
            
            Case: {case_id} in https://portal.mdintegrations.com/ is waiting for additional information. 
            Please login and check to review the details.

            Thanks & Regards,
            """
            send_text_email(sender=SENDER, recipient=recipient, subject=subject, content=content)
        elif 'case_assigned_to_clinician' == event_type:
            pass
        elif 'new_case_message' == event_type:
            logger.debug(f"new case message for {case_id}")
            case_data = self.get_case(case_id)
            if case_data.get('case_assignment') is not None:
                drname = case_data["case_assignment"]["clinician"]["full_name"]
                photourl = case_data["case_assignment"]["clinician"]["photo"]["url"]
                patient_name = case_data["patient"]["first_name"]
                html = get_mdintegration_case_message(patient_name, drname, photourl)
                send_html_email(sender=SENDER,
                                recipient=case_data["patient"]["email"],
                                subject='Next Medical New Message',
                                html=html)
                # send text message
                client.send_patient_message(patient_name, drname, case_data["patient"]["phone_number"], "webhook")
            else:
                logger.warning(f"{case_id} case_assignment is None")

        elif 'patient_modified' == event_type:
            pass
        else:
            logger.debug(f"unknown {event_type}")
            # raise Exception(f"unknown {event_type}")


class MDintegrationsChatAccutane(MDintegrationsChat):
    token_filename = 'mdi_token_accutane.json'
    client_id = CLIENT_ID_ACCUTANE
    client_secret = CLIENT_SECRET_ACCUTANE


class MDintegrationsChatDiagnostics(MDintegrationsChat):
    token_filename = 'mdi_token_diagnostics.json'
    client_id = CLIENT_ID_DIAGNOSTICS
    client_secret = CLIENT_SECRET_DIAGNOSTICS


class MDintegrationsChatWeightloss(MDintegrationsChat):
    token_filename = 'mdi_token_weightloss.json'
    client_id = CLIENT_ID_WEIGHTLOSS
    client_secret = CLIENT_SECRET_WEIGHTLOSS


class MDintegrationsChatTestosterone(MDintegrationsChat):
    token_filename = 'mdi_token_testosterone.json'
    client_id = CLIENT_ID_TESTOSTERONE
    client_secret = CLIENT_SECRET_TESTOSTERONE


class MDintegrationsChatCanada(MDintegrationsChat):
    token_filename = 'mdi_token_canada.json'
    client_id = CLIENT_ID_CANADA
    client_secret = CLIENT_SECRET_CANADA


class MDintegrationsChatAging(MDintegrationsChat):
    token_filename = 'mdi_token_aging.json'
    client_id = CLIENT_ID_AGING
    client_secret = CLIENT_SECRET_AGING


mdintegrations_api = MDintegrationsAPI(prod=is_prod)
mdintegrations_chat = MDintegrationsChat(prod=is_prod)
mdi_accutane = MDintegrationsChatAccutane(prod=is_prod)
mdi_weightloss = MDintegrationsChatWeightloss(prod=is_prod)
mdi_testosterone = MDintegrationsChatTestosterone(prod=is_prod)
mdi_canada = MDintegrationsChatCanada(prod=is_prod)
mdi_aging = MDintegrationsChatAging(prod=is_prod)
mdi_diagnostics = MDintegrationsChatDiagnostics(prod=is_prod)

# have mdi different instance mapping with test_type
mdi_instance_dict = {
    'normal': mdintegrations_chat,
    'accutane': mdi_accutane,
    'weightloss': mdi_weightloss,
    'testosterone': mdi_testosterone,
    'canada': mdi_canada,
    'aging': mdi_aging,
    'diagnostics': mdi_diagnostics
}


def detect_mdi_account_type(db_session: Session, patient_id: str):
    """detect_mdi_account_type for a patient_id"""
    if not patient_id or patient_id == 'None':
        return None, None
    try:
        db_mapping = MDIMappingCrud.fetch_by_patient_id(db_session, patient_id)
        if db_mapping:
            return db_mapping.mdi_account_type, mdi_instance_dict.get(db_mapping.mdi_account_type)
    except Exception as e:
        logger.exception(e)

    for mdi_account_type, mdi_api in mdi_instance_dict.items():
        try:
            res = mdi_api.get_patient(patient_id)
            if 'patient_id' in res:
                logger.info(f"Detected MDI account type: {mdi_account_type} for patient_id_md: {patient_id}")
                try:
                    MDIMappingCrud.create_with_values(db_session,
                                                      patient_id=patient_id,
                                                      email=res.get('email'),
                                                      mdi_account_type=mdi_account_type)
                except Exception as e:
                    logger.exception(e)
                return mdi_account_type, mdi_api
        except Exception as e:
            logger.exception(e)
    return None, None


def detect_mdi_case_account_type(db_session: Session, case_id: str):
    """detect_mdi_account_type for a case_id"""
    if not case_id or case_id == 'None':
        return None, None

    try:
        db_mapping = MDICaseMappingCrud.fetch_by_case_id(db_session, case_id)
        if db_mapping:
            return db_mapping.mdi_account_type, mdi_instance_dict.get(db_mapping.mdi_account_type)
    except Exception as e:
        logger.exception(e)

    for mdi_account_type, mdi_api in mdi_instance_dict.items():
        try:
            res = mdi_api.get_case(case_id)
            if 'case_id' in res:
                logger.info(f"Detected MDI account type: {mdi_account_type} for case_id: {case_id}")
                try:
                    MDICaseMappingCrud.create_with_values(
                        db_session,
                        case_id=case_id,
                        patient_id=res.get('patient', {}).get('patient_id'),
                        mdi_account_type=mdi_account_type
                    )
                except Exception as e:
                    logger.exception(e)
                return mdi_account_type, mdi_api
        except Exception as e:
            logger.exception(e)
    return None, None


if __name__ == '__main__':
    patient = {
        "first_name": "Adam",
        "last_name": "Trial",
        "email": "adam@trial.com",
        "metadata": "patient number 201",
        "gender": 1,
        "phone_number": "651-754-3011",
        "phone_type": 2,
        "date_of_birth": "1988-01-01",
        "address": {
            "address": "1901 1st Avenue, New York, NY 10029",
            "zip_code": "12345",
            "city_name": "Tazlina",
            "state_name": "Alaska"
        },
    }

    # res = mdintegrations.create_file('C:\\Users\\Tarique\\Desktop\\kasa.JPG')
    # res = mdintegrations.add_file_to_case(case_id='5924e17d-a33e-42f7-bfc3-7c683b3c33b6',
    # file_id='afac6cf9-213b-4933-bdb9-28c0199d4e7f')
    case_message = {
        'from': 'support',
        'text': 'first message'
    }
    # mdintegrations_chat.fetch_access_token()
    # logger.debug(mdintegrations_chat.token)
    # res = mdintegrations_chat.create_messages(case_id='5924e17d-a33e-42f7-bfc3-7c683b3c33b6', data=case_message)
    # print(res)
    # res = mdintegrations_chat.get_messages(case_id='5924e17d-a33e-42f7-bfc3-7c683b3c33b6', channel='support')
    # res = mdintegrations.get_patient_cases(patient_id='6ca862e8-14f9-4566-8c22-d82844abd913')
    param = {
        'name': 'Curexa',
        'address': None
    }
    # res = mdintegrations_api.get_pharmacies(params=param)
    # res = mdintegrations_api.add_pharmacy_to_patient(patient_id='6ca862e8-14f9-4566-8c22-d82844abd913',
    #                                                 pharmacy_id=29992)
    data = {
        "search": "adam@trial.com"
    }
    # res = mdintegrations_api.create_patient(patient)
    # print(res)
    case_files = ['bb7e04f0-53d2-4af8-b28c-aab37ff912c6']
    questions = [
        {
            'question': "Testing",
            'answer': "Yes",
            'type': "string",
            'important': True,
        },
        {
            'question': "ABNORMAL RESULT",
            'answer': 'NO',
            'type': "string",
            'important': True,
        },
        {
            'question': "SYMPTOMS",
            'answer': '',
            'type': "string",
            'important': True,
        },
        {
            'question': "Pharmacy".upper(),
            'answer': 'Safeway, Arapahoe Avenue, Boulder, CO, USA, 80302',
            'type': "string",
            'important': True,
        },
    ]
    prescription = {
        'partner_medication_id': '6329f9-102d-4409-98c9-42883edbcc40',
    }
    case = {
        'patient_id': '074e642b-a7e9-405b-ae40-c59771d89f9e',
        'case_files': case_files,
        'case_questions': questions,
        'case_prescriptions': [prescription]
    }
    # res = mdintegrations_api.create_case(case)
    # res = mdintegrations_api.search_compounds()
    # print(res)
    '''res = mdintegrations_api.get_patient_cases('e43592c1-a8ca-4e0a-9a3a-7f579521c120')
    print(res)
    res = mdintegrations_api.get_case('7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1')
    print(res)
    res = mdintegrations_api.get_case_questions('7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1')
    print(res)
    res = mdintegrations_api.get_prescription('7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1')
    print(res)'''
    '''data = {'event_type': 'case_completed', 'case_id': '7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1',
            'metadata': None}
    mdintegrations_chat.handle_webhook(data)'''

    '''res = mdintegrations_api.get_case('7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1')
    print(pformat(res))
    res = mdintegrations_api.get_case_questions('7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1')
    print(pformat(res))
    res = mdintegrations_api.get_prescription('7720a06d-6aff-4a84-a2fa-a5e14ff9b3f1')
    res = mdintegrations_api.get_case_files('47942b86-2788-472d-a9bf-215ba1a09d73')'''
    #res = mdi_accutane.list_services()
    #print(pformat(res))
