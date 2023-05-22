import logging
import requests

# CLIENT_KEY = 'nextmed_test_6j2G6oPVaRqpKifQdEhxhsGdNDQjpPjD'
# CLIENT_SECRET = 'HBna1DYXmnjWgYh4yd0LKXxwoKb2ol3s'


PUBLIC_API_KEY = '222I8N3Y0751NWOB'
PRIVATE_API_KEY = 'Vk5qtIc3pk6FNLzFo6FO5VDSr6fR8z7W'

logger = logging.getLogger("fastapi")


class AFFIRM_API:
    def __init__(self):
        self.base_url = 'https://api.affirm.com/api/v2/'

    def _post_request_(self, uri, params=None, json=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri

        auth = (PUBLIC_API_KEY, PRIVATE_API_KEY)

        try:
            if json is None:
                res = requests.post(url, auth=auth, params=params)
            else:
                res = requests.post(url, auth=auth, params=params, json=json)
            logger.info(res.status_code)
            return res.json()
        except Exception as e:
            logger.exception(e)
            return {}

    def authorize_transaction(self, data):
        uri = 'transactions'

        return self._post_request_(uri, json=data)


affirm = AFFIRM_API()


# if __name__ == '__main__':
#     data = {
#         "order_id": "62365794"
#     }
#     res = curexa.order_status(data)
#     print(res)
