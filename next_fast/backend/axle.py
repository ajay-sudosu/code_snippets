import requests


api_headers = {'Authorization': 'ApiKey live_5c0d24d64b7747abb4d578f0ab9fd6f7',
               "Content-Type": "application/json"}


def get_axle_services(zipcode): 
    r = requests.get(f"https://api.axlehealth.com/v1/services?zip_code={zipcode}", headers=api_headers)
    return r.json()


def get_axle_availability(data):
    r = requests.post("https://api.axlehealth.com/v1/availability", data=data, headers=api_headers)
    print(data)
    print(r)
    return r.json()


def create_axle_patient(payload):
    r = requests.post(f"https://api.axlehealth.com/v1/patients", data=payload, headers=api_headers)
    return r.json()


def create_axle_address(payload):
    r = requests.post(f"https://api.axlehealth.com/v1/addresses", data=payload, headers=api_headers)
    return r.json()


def create_axle_visits(payload):
    r = requests.post(f"https://api.axlehealth.com/v1/visits", data=payload, headers=api_headers)
    return r.json()
