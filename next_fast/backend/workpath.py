import requests

CLIENT_ID = "293a54d8-5b0f-465f-96fa-25e009cf40e9"
CLIENT_SECRET = "b1EyBg*eKArW8lZz(W"

def get_token():
	r = requests.post("https://api.workpath.co/oauth/token", data={
		"grant_type": "client_credentials",
		"client_id": CLIENT_ID,
		"client_secret": CLIENT_SECRET
	})
	return r.json()["access_token"]

def workpath_create_patient(data):
	h = {"Authorization": f"Bearer {get_token()}"}
	r = requests.post("https://api.workpath.co/people", data=data, headers=h)
	return r.json()

def workpath_create_intake(data):
	h = {"Authorization": f"Bearer {get_token()}"}
	r = requests.post("https://api.workpath.co/intakes", data=data, headers=h)
	return r.json()