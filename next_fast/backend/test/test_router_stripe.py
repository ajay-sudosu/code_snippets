import sys
from pathlib import Path

# BASE_DIR = Path('__file__').resolve().parent.parent.parent
sys.path.insert(0, '/Users/zestgeek26/PycharmProjects/next-med-backend/backend')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_stripe_fetch_refund_endpoint():
    refund_id = "string"
    response = client.get(f"/stripe-fetch-refund?refund_id={refund_id}")
    assert response.status_code == 200

def test_stripe_fetch_all_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/stripe-fetch-all", json=data)
    assert response.status_code == 200

def test_create_stripe_card_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/create-stripe-card", json=data)
    assert response.status_code == 200

def test_create_stripe_card_endpoint():
    # todo: check what data is coming here; Also same function name is used above.
    data = {}
    response = client.post("/create-new-card", json=data)
    assert response.status_code == 200

def test_stripe_refund_endpoint():
    data = {
  "charge": "string",
  "amount": 0,
  "metadata": {},
  "payment_intent": "string",
  "reason": "string"
    }
    response = client.post("/stripe-refund", json=data)
    assert response.status_code == 200

def test_stripe_update_subsription_saving_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/stripe-update-subsription-saving", json=data)
    assert response.status_code == 200

def test_stripe_create_invoice_endpoint():
    # todo: check what data is coming here
    data = {}
    response = client.post("/stripe-create-invoice", json=data)
    assert response.status_code == 200

def test_stripe_create_invoice_endpoint():
    # todo: check what data is coming here; Also same function name is used above.
    data = {}
    response = client.post("/stripe-create-invoice-subscription", json=data)
    assert response.status_code == 200

def test_stripe_webhook():
    # todo: check what data is coming here
    data = {}
    response = client.post("/stripe-webhook", json=data)
    assert response.status_code == 200

def test_create_stripe_card_endpoint():
    # todo: check what data is coming here; Also same function name is used above.
    data = {}
    response = client.post("/stripe-new-payment-method", json=data)
    assert response.status_code == 200

def test_update_customers_default_card():
    data = {
          "mrn": "string",
          "token": "string"
        }
    response = client.post("/update-customer-default-card", json=data)
    assert response.status_code == 200

def test_stripe_pause_subscription_create():
    data = {
          "subscription_id": "string",
          "email": "string",
          "status": "string"
        }
    response = client.post("/stripe-pause-subscription-create", json=data)
    assert response.status_code == 200

def test_stripe_pause_subscription_update():
    data = {
          "subscription_id": "string",
          "status": "string"
        }
    response = client.post("/stripe-pause-subscription-update", json=data)
    assert response.status_code == 200
