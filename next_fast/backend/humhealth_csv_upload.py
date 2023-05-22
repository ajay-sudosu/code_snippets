from sqlalchemy import create_engine
import pandas as pd
import json
import csv
import logging
import pysftp
import os
from urllib.parse import urlparse
from logging.handlers import TimedRotatingFileHandler
from config import DB_USERNAME, DB_PASSWORD, DB_ENDPOINT, DB_NAME
from config import HUMHEALTH_USERNAME, HUMHEALTH_PASSWORD, HUMHEALTH_HOST

# logger configurations
logger = logging.getLogger('humhealth')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(log_dir, os.path.splitext(os.path.basename(__file__))[0] + '.log')
fh = TimedRotatingFileHandler(logging_file, when='D', interval=1, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

def db_connection():
    try:
        DATABASE_URL = create_engine(
            'mysql+pymysql://' + DB_USERNAME + ':' + DB_PASSWORD + '@' + DB_ENDPOINT + ':3306/' + DB_NAME)

        connection = DATABASE_URL.connect()
        return connection
    except Exception as e:
        logger.error(f"Error while connection to database- {e}")

def generate_patient_rpm_enrollment_csv(local_path):
    """Function generating csv for patient and rpm enrollment."""
    try:
        connection = db_connection()
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        tables = ["rpm_patient_enrollment", "rpm_program_enrollment"]
        logger.info("Process for rpm_patient_enrollment starting")
        patient_enrollment_df = pd.read_sql_table(tables[0], connection)
        rpm_enrollment_df = pd.read_sql_table(tables[1], connection)
        with open(os.path.join(local_path, "humhealth_data.csv"), 'w', newline='', encoding='utf-8') as file:

            #  patient enrollment
            for index, column in patient_enrollment_df.iterrows():
                writer = csv.writer(file)
                writer.writerow(column.values)

            #  rpm enrollment
            for index, column in rpm_enrollment_df.iterrows():
                writer = csv.writer(file)
                writer.writerow(column.values)
        logger.info('CSV is ready.')
        return True
    except Exception as e:
        logger.error(f"generate_patient_rpm_enrollment_csv error - str{e}")


class Sftp:
    def __init__(self, hostname, username, password, port=22):
        """Constructor Method"""
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.cnopts = pysftp.CnOpts()
        self.cnopts.hostkeys = None

    def connect(self):
        """Connection to the sftp server."""

        try:
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port, cnopts=self.cnopts
            )
        except Exception as e:
            logger.error(f'connection fails - {e}')
        finally:
            logger.info(f"Connected to {self.hostname} as {self.username}.")

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()
        logger.info(f"Disconnected from host {self.hostname}")

    def upload(self, source_local_path, remote_path):
        """
        Uploads the source files to the sftp server.
        """
        try:
            logger.info(f"uploading to {self.hostname} as {self.username} in directory {remote_path}")
            self.connection.put(source_local_path, remote_path)
            logger.info("upload completed")
        except Exception as e:
            logger.error(f"upload fails- {e}")


if __name__ == '__main__':
    try:
        ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
        upload_path = "/home/nextmed/enrollment/unprocessed"
        local_path = os.path.join(ROOT_DIRECTORY, "humhealth_csv")
        logger.info("Generating csv.")
        generate_patient_rpm_enrollment_csv(local_path)
        logger.info("Csv has been generated successfully now starting the sftp process.")
        sftp_url = f"sftp://{HUMHEALTH_USERNAME}:{HUMHEALTH_PASSWORD}@{HUMHEALTH_HOST}"
        parsed_url = urlparse(sftp_url)
        sftp = Sftp(
            hostname=parsed_url.hostname,
            username=parsed_url.username,
            password=parsed_url.password,
        )
        # Connect to SFTP
        logger.info("Connecting to sftp server.")
        sftp.connect()
        logger.info("Connected successfully.")
        sftp.upload(os.path.join(local_path, "humhealth_data.csv"), os.path.join(upload_path, "humhealth_data.csv"))
        sftp.disconnect()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
