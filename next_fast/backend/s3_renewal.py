"""Module to re-generate the S3 file url since url expires every 7th day."""
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import pymysql
from urllib.parse import urlparse
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from config import DB_ENDPOINT, DB_USERNAME, DB_PASSWORD, DB_NAME

logger = logging.getLogger('s3_renewal')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(log_dir, os.path.splitext(os.path.basename(__file__))[0] + '.log')
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


class URLRenewal:
    def __init__(self):
        self.connection = pymysql.connect(DB_ENDPOINT, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME)

    def get_visit_rows(self, col):
        """get rows from visits table."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_query = f"""SELECT mrn, {col} FROM visits WHERE {col} IS NOT NULL"""
                cursor.execute(sql_query, ())
            return cursor.fetchall()
        except Exception as e:
            logger.exception(e)
            return []

    def update_visits_row(self, col: str, mrn: str, val: str):
        """Update visits table row with res."""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql_update_query = f"""update visits set {col}=%s where mrn=%s"""
                input_data = (val, mrn)
                cursor.execute(sql_update_query, input_data)
            self.connection.commit()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    @staticmethod
    def get_doc_id(url):
        o = urlparse(url)
        return o.path.strip('/')

    @staticmethod
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

    def renew_drchrono_req_res(self, col):
        rows = self.get_visit_rows(col)
        for row in rows:
            logger.debug(row)
            try:
                mrn = row.get('mrn')
                url = row.get(col)
                doc_name = self.get_doc_id(url)
                new_url = self.get_s3_url(doc_name)
                if new_url is not None:
                    logger.debug(f"updating {col} for mrn={mrn}")
                    self.update_visits_row(col=col, mrn=mrn, val=new_url)
            except Exception as e:
                logger.exception(e)

    def workflow(self):
        try:
            self.renew_drchrono_req_res('drchrono_req')
            self.renew_drchrono_req_res('drchrono_res')
        except Exception as e:
            logger.exception(e)
        finally:
            self.connection.close()


def main():
    urlrenewal = URLRenewal()
    urlrenewal.workflow()


if __name__ == '__main__':
    main()
