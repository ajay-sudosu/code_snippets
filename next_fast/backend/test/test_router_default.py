import sys
from pathlib import Path

# BASE_DIR = Path('__file__').resolve().parent.parent.parent
sys.path.insert(0, '/Users/zestgeek26/PycharmProjects/next-med-backend/backend')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_add_intake_eligibility_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/add-intake-eligibility", json=data)
    assert response.status_code == 200

def test_add_case_to_support_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/update-has-reviewed'", json=data)
    assert response.status_code == 200

def test_add_case_to_support_endpoint():
    # todo: check what data is coming here: Function named defined again
    data = {}
    response = client.post("/update-consumer-notes-complaints", json=data)
    assert response.status_code == 200

def test_upload_file_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/upload-file", json=data)
    assert response.status_code == 200

def test_update_pdf_file_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/sign-contract", json=data)
    assert response.status_code == 200

def test_upload_document_file_endpoint():
    # todo: Data is coming from a form,check upload file; Function name defined again
    data = {"req_type": "string",
            "mrn": "string",
            "document": "Upload a file"}

    response = client.post("/upload-document-drchrono-req-res", json=data)
    assert response.status_code == 200

def test_add_patient_weight():
    data = {
      "mrn": "string",
      "weight": 0
    }
    response = client.post("/add-patient-weight", json=data)
    assert response.status_code == 200

def test_get_patient_weight():
    mrn = "string"
    response = client.get(f"/get-patient-weight/{mrn}")
    assert response.status_code == 200

def test_update_patient_weight():
    data = {
      "mrn": "string",
      "weight": 0
    }
    response = client.post("/update-patient-weight", json=data)
    assert response.status_code == 200

def test_delete_patient_weight():
    data = {}
    response = client.delete(f"/delete-patient-weight/{mrn}")
    assert response.status_code == 200

def test_add_social_events():
    data = {
  "title": "string",
  "start_date_time": "string",
  "end_date_time": "string",
  "description": "string",
  "event_photo": "string",
  "location": "string",
  "event_members": [
        {
          "status": "going",
          "mrn": "string"
        }
        ]
    }
    response = client.post("/add-social-event", json=data)
    assert response.status_code == 200




