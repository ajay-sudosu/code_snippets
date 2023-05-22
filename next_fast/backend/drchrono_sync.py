"""Module to sync lab test results from drchrono api to database"""
import json
import os
import requests
import boto3
import base64
from botocore.client import Config
from botocore.exceptions import ClientError
from drchrono import drchrono
from db_client import DBClient
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from mdintegrations import mdintegrations_api
from urllib.parse import urlparse, parse_qs

HOURS_DELTA = 6

logger = logging.getLogger('drchrono_sync')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

logging_file = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(__file__))[0] + '.log')
fh = TimedRotatingFileHandler(logging_file, when='D', interval=1, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

s3_bucket = 'drchronodoc'
s3_client = boto3.client(
    's3',
    region_name='us-east-2',
    aws_access_key_id="AKIAJSZRUVGIPVVOPUGA",
    aws_secret_access_key="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",
    config=Config(signature_version='s3v4')
)

OBSERVATION_TO_TEST_NAME = {
    # Quest
    'Color Ur': 'Color',
    'Appearance Ur': 'Appearance',
    'Sp Gr Ur Strip': 'Specific Gravity',
    'pH Ur Strip': 'pH',
    'Glucose Ur Ql Strip': 'Glucose',
    'Bilirub Ur Ql Strip': 'Bilirubin',
    'Ketones Ur Ql Strip': 'Ketones',
    'Hgb Ur Ql Strip': 'Occult Blood',
    'Prot Ur Ql Strip': 'Protein',
    'Nitrite Ur Ql Strip': 'Nitrite',
    'Leukocyte esterase Ur Ql Strip': 'Leukocyte Esterase',
    'WBC #/area UrnS HPF': 'White Blood Cells',
    'RBC #/area UrnS HPF': 'Red Blood Cells',
    'Squamous #/area UrnS HPF': 'Squamous Epithelial Cells',
    'Bacteria #/area UrnS HPF': 'Bacteria',
    'Hyaline Casts #/area UrnS LPF': 'Hyaline Cast',
    'HSV1 IgG Ser IA-aCnc': 'Herpes 1',
    'HSV2 IgG Ser IA-aCnc': 'Herpes 2',
    'HIV 1+2 Ab+HIV1 p24 Ag SerPl Ql IA': 'HIV AG/AB, 4th Gen',
    'C trach rRNA Spec Ql NAA+probe': 'Chlamydia',
    'N gonorrhoea rRNA Spec Ql NAA+probe': 'Gonorrhea',
    'T vaginalis rRNA Spec Ql NAA+probe': 'Trichomoniasis',
    'RPR Ser Ql': 'RPR (Syphilis), with Reflex',
    'HBV surface Ag SerPl Ql IA': 'Hepatitis B',
    'HCV Ab SerPl Ql IA': 'Hepatitis C',
    'HCV Ab s/co SerPl IA': 'Hepatitis C',
    'M hominis Spec Ql Cult': 'Mycoplasma',
    'Ureaplasma Spec Cult': 'Ureaplasma',
    'HSV1 IgM Ser Ql IF': 'Herpes 1',
    'HSV2 IgM Ser Ql IF': 'Herpes 2',
    'HIV1 RNA # SerPl NAA+probe': 'HIV',
    'HIV1 RNA SerPl Ql NAA+probe': 'HIV',

    # Labcorp
    'Urine-Color': 'Color',
    'Appearance': 'Appearance',
    'Specific Gravity': 'Specific Gravity',
    'pH': 'pH',
    'Glucose': 'Glucose',
    'Bilirubin': 'Bilirubin',
    'Ketones': 'Ketones',
    'Occult Blood': 'Occult Blood',
    'Protein': 'Protein',
    'Nitrite, Urine': 'Nitrite',
    'WBC Esterase': 'WBC Esterase',
    'Urobilinogen,Semi-Qn': 'Urobilinogen',
    'WBC': 'White Blood Cells',
    'RBC': 'Red Blood Cells',
    'Epithelial Cells (non renal)': 'Epithelial Cells',
    'Bacteria': 'Bacteria',
    'Casts': 'Casts',
    'HSV 1 IgG, Type Spec': 'Herpes 1',
    'HSV 2 IgG, Type Spec': 'Herpes 2',
    'HIV Screen 4th Generation wRfx': 'HIV AG/AB, 4th Gen',
    'Chlamydia by NAA': 'Chlamydia',
    'Gonococcus by NAA': 'Gonorrhea',
    'Trich vag by NAA': 'Trichonomiasis',
    'HBsAg Screen': 'Hepatitis B',
    'HCV Ab': 'Hepatitis C',
    'Mycoplasma hominis': 'Mycoplasma Culture',
    'Ureaplasma urealyticum': 'Ureaplasma',
}
# convert all keys to lower case
OBSERVATION_TO_TEST_NAME = {k.lower(): v for k, v in OBSERVATION_TO_TEST_NAME.items()}


def fetch_lab_orders():
    """Fetch lab orders generated within last hour"""
    lastHourDateTime = datetime.datetime.now() - datetime.timedelta(hours=HOURS_DELTA)
    param = {
        'since': lastHourDateTime.strftime('%Y-%m-%dT%H:%M:00')
    }

    res = drchrono.lab_orders_list(param)
    logging.debug(res)

    return res.get('results', [])


def get_patient_name_dob(patient_id):
    """Fetch patient's details & return name & dob"""
    res = drchrono.patients_read(patient_id)
    logging.debug(res)

    return res.get('first_name', '')


def fetch_lab_results(lab_order_id):
    """Fetch lab results"""
    results = []
    cursor = None
    while True:
        param = {
            'cursor': cursor,
            'order': lab_order_id
        }

        res = drchrono.lab_results_list(param)
        logging.debug(res)
        results += res.get('results', [])
        url = res.get('next')
        if url is None:
            return results
        else:
            parsed_url = urlparse(url)
            cursor = parse_qs(parsed_url.query)['cursor'][0]
            logger.debug(f'cursor={cursor}')


def is_results_final(lab_results):
    """Returns False if any result status is P or I else return True"""
    tests_dict = {}
    for result in lab_results:
        test = result.get('observation_description')
        status = result.get('status')
        tests_dict[test] = result.get('status')
    for status in tests_dict.values():
        if status == 'P' or status == 'I':
            return False
    return True


def get_abnormal_results(lab_results):
    """returns a list of Tests with abnormal results"""
    abnormal_tests = []

    for result in lab_results:
        if result.get('is_abnormal') is True:
            logger.debug(f"Abnormal result found: {result} ")
            # find lab test
            observation_description = result.get('observation_description')
            lab_test_name = OBSERVATION_TO_TEST_NAME.get(observation_description.lower(), "")
            if lab_test_name == "":
                logger.warning(f"Lab Test name not found for observation_description:{observation_description}")
                continue
            if lab_test_name not in abnormal_tests:
                abnormal_tests.append(lab_test_name)

    return abnormal_tests


def fetch_lab_documents():
    """Fetch lab documents generated within last hour"""
    lastHourDateTime = datetime.datetime.now() - datetime.timedelta(hours=HOURS_DELTA)
    cursor = None
    documents = []
    while True:
        param = {
            'cursor': cursor,
            'since': lastHourDateTime.strftime('%Y-%m-%dT%H:%M:00')
        }
        res = drchrono.lab_documents_list(param)
        documents += res.get('results', [])
        url = res.get('next')
        if url is None:
            return documents
        else:
            parsed_url = urlparse(url)
            cursor = parse_qs(parsed_url.query)['cursor'][0]
            logger.debug(f'cursor={cursor}')
    return []


def download_pdf(document_id, url):
    pdf_path = f'pdfs/drchrono_documents/{document_id}.pdf'
    try:
        logger.debug(f"downloading pdf {document_id}")
        response = requests.get(url)
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        f.close()

        return pdf_path
    except Exception as e:
        logger.exception(e)
        return None


def upload_file(file_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, s3_bucket, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True


def get_s3_url(filename):
    try:
        # Generate the URL to get 'key-name' from 'bucket-name'
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': s3_bucket,
                'Key': filename
            },
            ExpiresIn=3600 * 24 * 7 - 1
        )
    except Exception as e:
        logger.exception(e)
        return None
    return url


def send_results_to_mdintegrations(pharmacy, md_patient_id, pdf_path, abnormal_result):
    try:
        if abnormal_result is None:
            abnormal_result = 'NO'
        else:
            abnormal_result = 'YES'
        questions = [
            {
                'question': "RESULT REVIEW",
                'answer': "REVIEW RESULTS",
                'type': "string",
                'important': True,
            },
            {
                'question': "ABNORMAL RESULT",
                'answer': abnormal_result,
                'type': "string",
                'important': True,
            },
            {
                'question': "Pharmacy",
                'answer': pharmacy,
                'type': "string",
                'important': True,
            },
        ]
        data = {
            'patient_id': md_patient_id,
            'case_questions': questions,
        }
        if os.path.exists(pdf_path):
            logger.debug(f"Creating file on mdintegrations: {pdf_path}")
            with open(pdf_path, 'rb') as f:
                response = mdintegrations_api.create_file(f)
                logger.debug(response)
                file_id = response.get('file_id')
            if file_id is not None:
                logger.debug(f"creating case on mdintegrations...")
                response = mdintegrations_api.create_case(data)
                logger.debug(response)
                case_id = response.get('case_id')
                logger.debug(f"adding file: {file_id} to case: {case_id}...")
                res = mdintegrations_api.add_file_to_case(case_id, file_id)
                logger.debug(res)
                return True
    except Exception as e:
        logger.exception(e)
    return False


def main():
    logger.info("Started")
    db = DBClient()
    arr = []
    for lab_doc in fetch_lab_documents():
        logger.debug(lab_doc)
        lab_order_id = lab_doc.get("lab_order")
        lab_order = drchrono.lab_orders_read(lab_order_id)
        patient_id = lab_order.get('patient')
        if patient_id is None:
            logger.debug("patient_id is None. skipping...")
            continue

        visit_data = db.get_visits_by_patient_id(patient_id)
        visit = visit_data.get("data")
        if visit is None:
            logger.debug("visit is None. skipping...")
            continue
        mrn = visit.get("mrn")
        email = visit.get("email")
        name = visit.get("patient_name")
        phone = visit.get("phone")
        md_patient_id = visit.get("patient_id_md")
        pharmacy = visit.get("pharmacy")
        notify_sent = visit.get("drchrono_result_notify")
        result_to_mdint = visit.get("drchrono_result_to_mdint")
        drchrono_res_ts = visit.get("drchrono_res_ts")
        drchrono_req_ts = visit.get("drchrono_req_ts")
        if phone[0] == "1":
            phone = phone[1:]

        doc_ts = lab_doc.get("timestamp")
        doc_timestamp = datetime.datetime.strptime(doc_ts, '%Y-%m-%dT%H:%M:%S')
        doc_type = lab_doc.get("type")
        document = lab_doc.get("document")
        document_id = lab_doc.get("id")
        pdf_path = download_pdf(document_id, document)

        if doc_type == 'REQ':
            if drchrono_req_ts is not None:
                drchrono_req_timestamp = datetime.datetime.strptime(drchrono_req_ts, '%Y-%m-%dT%H:%M:%S')
                if drchrono_req_timestamp >= doc_timestamp:
                    logger.debug(f"Not a newer REQ: {document_id}. Skipping...")
                    continue
            # upload to S3
            if upload_file(pdf_path):
                file_url = get_s3_url(f'{document_id}.pdf')
            else:
                continue
            logger.info(f"Updating visits table with req for mrn={mrn}, req={file_url}, ts={doc_ts}")
            db.update_visits_drchrono_req(req=file_url, ts=doc_ts, mrn=mrn)
        elif doc_type == 'RES':
            if drchrono_res_ts is not None:
                drchrono_res_timestamp = datetime.datetime.strptime(drchrono_res_ts, '%Y-%m-%dT%H:%M:%S')
                if drchrono_res_timestamp >= doc_timestamp:
                    logger.debug(f"Not a newer RES: {document_id}. Skipping...")
                    continue
            # upload to S3
            if upload_file(pdf_path):
                file_url = get_s3_url(f'{document_id}.pdf')
            else:
                continue
            if result_to_mdint != "sent":
                result_json = fetch_lab_results(lab_order_id)
                if not is_results_final(result_json):
                    logger.debug(f"Some results in P/I status for lab_order: {lab_order_id}. skipping...")
                    continue
                else:
                    logger.debug(f"All results in Final status for lab_order: {lab_order_id}.")

                abnormal_tests = get_abnormal_results(result_json)
                if len(abnormal_tests) > 0:
                    abnormal_tests_str = ';'.join(abnormal_tests)
                    logger.info(
                        f"Updating visits table with drchrono_abnormal_tests={abnormal_tests_str} for mrn={mrn}")
                    db.update_visits_drchrono_abnormal_tests(tests=abnormal_tests_str, mrn=mrn)
                else:
                    abnormal_tests_str = None
                # sent = send_results_to_mdintegrations(pharmacy, md_patient_id, pdf_path, abnormal_tests_str)
                if sent:
                    logger.info(f"Updating visits table with drchrono_result_to_mdint to 'sent' for mrn={mrn}")
                    db.update_visits_drchrono_result_to_mdint(mrn=mrn, sent=True)

            logger.info(f"Updating visits table with res for mrn={mrn}, res={file_url}, ts={doc_ts}")
            db.update_visits_drchrono_res(res=file_url, ts=doc_ts, mrn=mrn)
            try:
                if notify_sent != "sent":
                    db.send_patient_message(name, "Dr. Marc Serota", phone, "result")
                    db.update_visits_drchrono_result_notify(mrn=mrn, sent=True)
            except Exception as e:
                logger.exception(e)
        else:
            logger.info(f"unknown type={doc_type}")

        try:
            logger.debug(f"Deleting downloaded pdf {pdf_path}")
            os.remove(pdf_path)
        except Exception as e:
            logger.exception(e)

    logger.info("Finished")


def main_old():
    logger.info("Started")
    db = DBClient()
    drchrono_lab_orders = db.get_drchrono_lab_orders()
    logger.debug(drchrono_lab_orders)
    order_id_list = [x['lab_order_id'] for x in drchrono_lab_orders["data"]]

    for lab_order in fetch_lab_orders():
        patient_id = lab_order.get('patient')
        if patient_id is None:
            logger.debug("patient_id is None. skipping...")
            continue
        lab_order_id = lab_order.get('id')

        # if this order is already in drchrono_lab_orders then continue
        if lab_order_id in order_id_list:
            logger.debug(f"{lab_order_id} already in drchrono_lab_orders")
            continue

        # fetch visit for this patient from db
        timestamp = lab_order.get('timestamp')
        dt_ts = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        # try 3 days to find a visit match
        for i in [0, 24, 48]:
            dt = dt_ts - datetime.timedelta(hours=i)
            visits_res = db.get_visits_by_patient_id_date(patient_id, dt.year, dt.month, dt.day)
            visits = visits_res["data"]
            logger.debug(visits)
            if len(visits) == 0:
                continue
            # match order with visit
            visit = visits[0]

            # add order to db
            visit_id = visit.get('mrn')
            db.insert_drchrono_lab_orders(lab_order_id, visit_id)
            break
        else:
            logger.warning("Couldn't find a visit match.")

    drchrono_lab_orders_res = db.get_drchrono_lab_orders()
    drchrono_lab_orders = drchrono_lab_orders_res["data"]
    logger.debug(drchrono_lab_orders)
    # Do for all orders in queue
    for lab_order in drchrono_lab_orders[:]:
        # fetch result
        results = fetch_lab_results(lab_order.get('lab_order_id'))
        logger.debug(results)
        if len(results) == 0:
            continue

        # update visits table with results
        mrn = lab_order.get('visit_id')
        logger.debug(f"Updating results for {mrn}")
        result = db.update_visits_results(results=json.dumps(results), mrn=mrn)
        logger.info(result)

        for result in results:
            if result.get('status') != 'F':
                logger.info("Updating visits table with status")
                # update visits table with status
                db.update_visits_status(mrn=lab_order.get('visit_id'), status=result.get('status'))
                break
        else:
            logger.info(f"Updating visits table with status 'F' for {mrn}")
            # update visits table with status 'F'
            result = db.update_visits_status(mrn=mrn, status='F')
            logger.info(result)
            # remove from queue
            drchrono_lab_orders.remove(lab_order)
            # remove from db
            db.delete_drchrono_lab_orders(lab_order.get('lab_order_id'), lab_order.get('visit_id'))


def test_get_abnormal_results():
    result_json = fetch_lab_results(5545358)
    ab = get_abnormal_results(result_json)
    print(ab)


if __name__ == '__main__':
    main()
    # test_get_abnormal_results()
