from email.quoprimime import body_check
import requests
import logging

logger = logging.getLogger("fastapi")
Authorization_token = 'ZFNNTmsxMXM5cnR1UnozUlVRUA=='


class FreshDeskAPI:

    def __init__(self):
        self.base_url = 'https://joinnextmed.freshdesk.com'
        self.session = requests.Session()
        self.session.headers.update({'Authorization': Authorization_token})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.session.headers.update({'Accept': '*/*'})
        self.session.headers.update({'Cookie': '_x_w=43_1'})

    def _post_request_(self, url, json=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        res_obj = self.session.post(url, json=json)
        return res_obj.json()
     
    def _get_request_(self, url):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        res_obj = self.session.get(url)
        return res_obj.json()
     
    def create_ticket(self, body: dict):
        """Create ticket"""
        url = 'https://joinnextmed.freshdesk.com/api/v2/tickets'
        return self._post_request_(url, json=body)
        
    def view_ticket(self, ticket_id):
        """View ticket"""
        url = f'https://joinnextmed.freshdesk.com/api/v2/tickets/{ticket_id}'
        return self._get_request_(url) 
        
    def view_conversation(self, ticket_id):
        """View ticket"""
        url = f'https://joinnextmed.freshdesk.com/api/v2/tickets/{ticket_id}/conversations'
        return self._get_request_(url) 

    def reply_ticket(self, body:dict):
        """View ticket"""
        if "ticket_id" in body: 
         ticket_id = body["ticket_id"]
         del body["ticket_id"]
        url = f'https://joinnextmed.freshdesk.com/api/v2/tickets/{ticket_id}/reply'
        return self._post_request_(url,json=body) 
        

fr_api = FreshDeskAPI()
