import pytest
from mdintegrations import detect_mdi_case_account_type, detect_mdi_account_type


@pytest.mark.skip
def test_detect_mdi_account_type():
    mdi_account_type, mdi_api = detect_mdi_account_type(None)
    assert mdi_account_type is None
    assert mdi_api is None

    mdi_account_type, mdi_api = detect_mdi_account_type('None')
    assert mdi_account_type is None
    assert mdi_api is None

    mdi_account_type, mdi_api = detect_mdi_account_type('6ca862e8-14f9-4566-8c22-d82844abd913')
    assert mdi_account_type == 'normal'


def test_detect_mdi_case_account_type():
    mdi_account_type, mdi_api = detect_mdi_case_account_type(None)
    assert mdi_account_type is None
    assert mdi_api is None

    mdi_account_type, mdi_api = detect_mdi_case_account_type('None')
    assert mdi_account_type is None
    assert mdi_api is None

    mdi_account_type, mdi_api = detect_mdi_case_account_type('5924e17d-a33e-42f7-bfc3-7c683b3c33b6')
    assert mdi_account_type == 'normal'
