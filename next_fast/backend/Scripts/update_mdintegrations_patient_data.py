import logging

from db_client import DBClient
from mdintegrations import mdi_instance_dict

logger = logging.getLogger("fastapi")


def get_mdi_patients_list():
    """
    Get patients data from visits table when patient_id_md is not None, "" or 0 and
    update medications and allergies on mdi
    """
    try:
        client = DBClient()
        patient_data = client.get_visits_data_for_patient_id_md()
        for item in patient_data.get('data', []):
            test_type = item.get("patient_test_type", "normal")
            mdintegrations_api = mdi_instance_dict.get(test_type)
            medication = item.get('current_medications', None)
            if medication not in [None, 'None', '', ' ']:
                mdintegrations_api.update_patient(item.get('patient_id_md'), {"current_medications": medication})
            allergies = item.get('allergies', None)
            if allergies not in [None, 'None', '', ' ']:
                mdintegrations_api.update_patient(item.get('patient_id_md'), {"allergies": allergies})
    except Exception as e:
        print(e)


if __name__ == '__main__':
    get_mdi_patients_list()
