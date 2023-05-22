import logging
import requests

# CLIENT_KEY = 'nextmed_test_6j2G6oPVaRqpKifQdEhxhsGdNDQjpPjD'
# CLIENT_SECRET = 'HBna1DYXmnjWgYh4yd0LKXxwoKb2ol3s'


CLIENT_KEY = 'nextmed_live_MJJXyzNZjlkDrvw4KmLVN8Th3QvRN1Zj'
CLIENT_SECRET = 'OPwU4Q1KwxpouD0LCP7dNOQD5KYKfspP'

logger = logging.getLogger("fastapi")


class CurexaAPI:
    def __init__(self):
        self.base_url = 'https://api.curexa.com'

    def _post_request_(self, uri, params=None, json=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri

        auth = (CLIENT_KEY, CLIENT_SECRET)

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

    def create_order(self, data):
        uri = '/orders'

        return self._post_request_(uri, json=data)

    def order_status(self, order_id):
        uri = '/order_status'

        data = {
            "order_id": order_id
        }

        return self._post_request_(uri, json=data)

    def cancel_order(self, data):
        uri = '/cancel_order'

        return self._post_request_(uri, json=data)


curexa = CurexaAPI()


if __name__ == '__main__':
    data = {
        "order_id": "62365794"
    }
    res = curexa.order_status(data)
    print(res)
