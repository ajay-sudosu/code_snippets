import pytest
from routers.router_mdi import (
    detect_mdi_account_type, get_prescriptions_from_dict, read_jsonfile
)
from pathlib import Path


@pytest.mark.skip()
def test_detect_mdi_account_type():
    assert None, None == detect_mdi_account_type('')


def test_get_prescriptions_from_dict():
    medicines = [{'month': 1, 'curr_dose': 0, 'medication_id': ['751cd822-c6f2-47b0-8064-890817fc10ff', '8d9667db-198a-4c33-955c-7b46a7c33cf2'], 'compound_id': ['a54c552f-c810-4b5e-8af0-dc713c25dc9b']}, {'month': 3, 'curr_dose': 0, 'medication_id': ['67e0770f-1451-4a86-b056-183d2dd08c69', '938d26c0-7dde-4bd4-98c5-2c7ad25a1f62'], 'compound_id': ['c02e95ff-60de-4530-8698-12bd620a2ec5']}, {'month': 3, 'curr_dose': 1, 'medication_id': ['67e0770f-1451-4a86-b056-183d2dd08c69', '938d26c0-7dde-4bd4-98c5-2c7ad25a1f62'], 'compound_id': ['c02e95ff-60de-4530-8698-12bd620a2ec5']}, {'month': 6, 'curr_dose': 0, 'medication_id': ['65c27dba-6640-495d-aa87-bd2cc9de0d6d', 'ea735bc9-6a9a-487d-8842-b465a24d45ee'], 'compound_id': ['277ca4a4-2385-48ec-9fd6-7c97b5bb3791']}, {'month': 6, 'curr_dose': 1, 'medication_id': ['65c27dba-6640-495d-aa87-bd2cc9de0d6d', 'ea735bc9-6a9a-487d-8842-b465a24d45ee'], 'compound_id': ['277ca4a4-2385-48ec-9fd6-7c97b5bb3791']}, {'month': 6, 'curr_dose': 2, 'medication_id': ['65c27dba-6640-495d-aa87-bd2cc9de0d6d', 'ea735bc9-6a9a-487d-8842-b465a24d45ee'], 'compound_id': ['277ca4a4-2385-48ec-9fd6-7c97b5bb3791']}]
    expected_case_prescriptions = [
        {'partner_medication_id': '751cd822-c6f2-47b0-8064-890817fc10ff'},
        {'partner_medication_id': '8d9667db-198a-4c33-955c-7b46a7c33cf2'},
        {'partner_compound_id': 'a54c552f-c810-4b5e-8af0-dc713c25dc9b'}
    ]
    curr_dose = 0
    weight_loss_month = 1
    case_prescriptions = get_prescriptions_from_dict(medicines, curr_dose, weight_loss_month)
    assert case_prescriptions == expected_case_prescriptions


def test_read_jsonfile():
    filename1 = Path('mdi_data/customer_nextmed.json')
    filename2 = Path('mdi_data/customer_weightloss.json')
    mdi_medication_dict = read_jsonfile(filename1)
    assert type(mdi_medication_dict) is dict
    mdi_medication_dict = read_jsonfile(filename2)
    assert type(mdi_medication_dict) is dict
