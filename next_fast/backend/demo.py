# import requests

# url = "https://api.mdintegrations.com/v1/partner/files"

# access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIwN2ExYjgzMy0xYWEyLTQ5MzgtYTJhZi00YmFjNmRiZThjOTUiLCJqdGkiOiIyYWFlZmM5YWUxN2E0YTFhYzEyYjk0ODNkYTRkNjUyYmI3YzAwZTZlZDExZjlkNzdkNzVlOWM0NDc0ODAyY2IxMjc1MjIyNTNlMjNkYzc3MiIsImlhdCI6MTY1NTkxNDU2Ny42MDc4MzYsIm5iZiI6MTY1NTkxNDU2Ny42MDc4MzksImV4cCI6MTY1NjAwMDk2Ny42MDQ3OTEsInN1YiI6IiIsInNjb3BlcyI6WyIqIl19.Ba756nYk6qQNLC_SdszL98J-GrlSFzNK0mchqyrh-eqDI5uHMC_66NnO4anaua-2ogAjA1_0-CcBi4fX2Bdh1FGM8JbI_Cf2NFsWBDUh8y7GyG3Bie_qKG-OaHFFKo7GXuvQNZUu0EtsnfY96HK6WzLvdHt-ZexU6GkK-bm6OVrt9mKWYyIRZZqzrwoXXgTDf-XmYNaSbJWmPvKc-QPLmyI-sUSVJvLQ80-wAjcSIFaDt171H-OFkZo1Mqev40sIb7X1NbN6TjDPY-XHw70HRQVkLssF65P6PI6EYw8xHuykikMHh0sDGwYFj5B8TQyLQNnPmTrqScDHKIRIHK2jqpnpQtXGGNLRuuYMQuwWSryXpVB2ahupEjQbJPceuWIwE3_6_b0gksS4X9ryMM2idLrmw6KpT3-5R4_bno09X7u0ZuKgAUvxOoMPDOLU6wG3eWUAneCG924ew6NT2C6OxVny3gI26ob7WGaPg0du4KbFLUPI_9aAFxguv4ASbBWb-GSXe8lsEBNYtVUwnSwzXYf5yEmQxzCRtKbgM1atZppg_nJX7z3sClCqlAndJQjsT57pUqBnxGwTXovWqpruply2ZJ1RYKCaP0it79KlPVDDbcX5pNWtB-z_5zZOmdq0mVuMDbRoAeAxqOz1kqktNumOP7xqN551r_yQoXQXe0g"

# headers = {
#     'Authorization': f'Bearer {access_token}',
#     'Content': 'multipart/form-data;',
#     'Accept': 'application/json',
# }
# file_ = "covid.csv"
# files = {'file': open(file_, 'rb')}

# payload = {
#     'name': "results",
# }
# r = requests.post(url, files=files, headers=headers, data=payload)
# print(r.json())



# import requests
# import json
# import time
# # for i in range(300, 369):
# #     time.sleep(2)
#     # print("LOOP------------->", i)
# url = "https://www.covermymeds.com/ajax/list/"

# Cookie = "cookiesession1=678B286DA1521F78B88B8487C836C099; _gcl_au=1.1.1518087558.1654107891; _fbp=fb.1.1654107895039.1730448165; cmc_is_minimized=true; _gaexp=GAX1.2.DM0HnDDuSDWl6W033drI1A.19204.1; d-a8e6=bd0b1efd-7382-4ed3-ad01-5dd0460344f1; _dashboard_portal_session=RVFEb1NvVG9CMlpGQWhDa3BsalhPK1Z1cTNBVVZ0MEhFQWV4WVA0ZkRjYXhWMmtMbFZJL1RWNldZZWtUZUpUSmpvd0txaUplaHRDWUtuZUIwcnBSWFNJY1hxaW1kYWIxTzA4aUtHMVByMW1tT0oraDAyZXJzSGdOSHo1cndvcHJMM3N5UDdVdmtmZGs2dWV1Zm44ZWdRVUhVR2kwdFBnaGg5WEJTZnFkN0FOV3h6YVhHaHoydkM3dEpsSVVzN0E2M3hnRkhnQmw1ZGRuK0ZWTGwwb1BHL091elB5Z3JoTnhSM3dGYyt3ZC95V3BZR1dFRjdCbUVhN3FWdE1sLzljUGFtaVh2VXE3Yk9SM0hpQjdnd2taZlRsaHdTcWQzSnZOZ2s5blVJdFdBTGdYMlM0K1VBWHZ6aWhrWGl1dzVleGtIbzdUaitHYk9ZVlFzdmVVWXpnNURSRlNjc0ZKT3NwS2xjL1FUU0RRWCtkR3J4aDVZTDM0VGZsZjJRWTM3am1mdFZBdTVyQmozQmx6cHJTcU0zL1BUcCs1cFhSelVPNzBLUHduc3MvbGNrMlpwWnY3OTI1RXhUMGtEcDRkT3h4elZScUk0S3JWaUpHekRwd0xmWXVpdlNPS1lQZHozdklNbGJXSC9qVVZrQzJFTUNqSTNZSThqckh2MXlkK2NkYjJ1U0hhUm9rdXA5eWJyVHpEUWpBcjlMQTBLM21XMWpqaHF0eGlycWxGY09TVWwxMnF0dGJsY29EcWV4Q0FVeXFYVmwyeWpVNGxPZU9CSkxLbU5MSFh3a1dkZk8vaHpWakZVODdjZzdyRGlLdmhIK0p6cVB0cUI2cXhJdGM4QXRYajlEaHNRZSs1NHhueXQzcmYxYjdvZ0Nyc3A3eTV3MzNzcXYxZHE5aU9Idk1YYkZJS0lCanNLanQ5aU9UQWpCQmZGSzY4c01iQVpUZ1ZFeDQxY2hZVVRJaFVBdWpNSDdkcWk2UC8rdmZRTE9DRnJ0NTBoRWd5QU0yVURxVkFWTURUMkcybkVMdElFZUlzcGlPdWZFRVZ5NWFMVmdEYkN6aWJ3a1F0SHMrZlNocFN5TUtpSDFicFplbjlYa2lXWmx2Njd5elZLNTBVOFFSb2x0ei9oeDdMTkE9PS0tRyt0Q3dYYzhGTmJ3YktDcGphdFdudz09--c7c99630ece5b7af9455853cb87c324cf62f31ae; _gid=GA1.2.389189990.1656016268; _uetsid=6b06ad60f33311ec9e4a6531c07e3467; _uetvid=220e0540e1d811ecaf8755125c4e2cbc; _ga_FNV852Y540=GS1.1.1656016269.1.0.1656016275.0; _ga=GA1.2.1839524128.1654107895; InnovaApp=1i5h0ofqdtsra3jf7hdenhiui5; cmm_production_session=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiIsImtpZCI6ImVoNUNNQ1c4WlpJUHpxSlRRYWxLSUVabGFTTFV1SWFCZGNzamRqWHhQdmsifQ.eyJ1aWQiOjMwNDk3NTMsImZubSI6IkZyYW5rIExlb25hcmRvIiwidW5tIjoibmV4dG1lZGljYWwiLCJpc3MiOiJjbW1fcHJvZHVjdGlvbl9zZXNzaW9uIiwianRpIjoiNGY0OWM0NTgtYTMxMS00MGU2LWIwZTQtNDY0NjRiZTYwNWU2IiwiZXhwIjoxNjU2MDI3NDM0LCJ1Y28iOltdfQ.go-KLBCpiYt2P9WvpOgPhjNjjGJXpiglz9w0KoN3i6Mydp3soK5w2-OIK2rczATCnQDIZeYXThcs2Gp7D3AQUUOA-QMlwKU-VET0-06mAycvFQGedG_q-b1iy9FbOAA7L7sb9canfz7vGDPlvjffVOoaKk4z9euPme_I6X0G_fflcCBeyZ1dbXW4VdAOeAaovXb0QCTfVM6JTvWVOZ0E6imwn8Q65x7SDw_6CyhacQAWIkj3pdFSJTCIgOpwrnV4KhtoFIMibgpWqqfRWa4B2S2g8ptWg9cvAXZdUawbJNCbr4HBRuHEksU24GOerwB_0-AlKmqzWxc0u8pHCYBX5Du9Vv72g-Y-tKfyBfeDqG2x8x0-tQ3g648eOki6G4oaR10za0te4g7FHBnmsXDrJq_iY3lQs5HjetGrqi5ui_BdpCdDwCUvFe_WVu6jUUWA4keE1P6c_w5l3DBcBemPfIXNJJScXB3O-dSFoddv60xoRThY9kNVLvlnyfnGfUFH_5YVMzyCUpiT0rQvP-duAIMwaZ1j8Ik4ex_YNRnDe9TOUQVHJ-C8uIel_sNEdyjCMA8E6FvdTqimZxOJGkepTkfnqb85NLWCqNxslsOwW2AtLFDKs8s2qxLOE8pwPaNKYycURKPFEb3s680H6QnveFBkGCZTb2BapMoS9AHMNSQ"
# headers = {
#     "Accept": "*/*",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Connection": "keep-alive",
#     "Content-Length": "64",
#     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
#     "Cookie": Cookie,
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
#     }
# file_ = "covid.csv"
# files = {'file': open(file_, 'rb')}

# payload = {
#         'mode': 7,
#     'openPage': 1,
#     'closedPage': 1,
#     'searchPage': 369,
#     'pagesize': 4,
# } 
# r = requests.post(url, headers=headers, data=payload)
# json_obj = r.json()
# json_object = json.dumps(json_obj, indent = 4)

# # Writing to sample.json
# with open("data.json", "a") as outfile:
#     outfile.write(json_object)


import os
import selenium
from selenium import webdriver
import time
from PIL import Image
import io
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException


#Install Driver
driver = webdriver.Chrome(ChromeDriverManager().install())

url = "https://www.novocare.com/wegovy/cost-navigator.html"
driver.get(url)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)#sleep_between_interactions






