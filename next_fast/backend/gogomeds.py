import logging
import requests

# CLIENT_KEY = 'nextmed_live_MJJXyzNZjlkDrvw4KmLVN8Th3QvRN1Zj'
# CLIENT_SECRET = 'OPwU4Q1KwxpouD0LCP7dNOQD5KYKfspP'

logger = logging.getLogger("fastapi")


class GogoMedsAPI:
    def __init__(self):
        self.base_url = 'https://uat.gogomeds.com/gogomedsserver60'

    def authenticate(self):
        try:
            url = self.base_url + "/token"
            payload = "grant_type=password&username=testnexmed@gogomeds.com&password=@p!12#$tG1$"
            response = requests.post(url, data=payload)
            res = response.json()
            print("token", res.get("access_token"))
            return res.get("access_token")
        except Exception as e:
            logger.exception(e)
            return {}

    def _make_request_(self, uri, params=None, json=None, method=None):
        """
        Send a requests.post request
        :param uri: Endpoint URI
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url + uri

        headers = {
            'Authorization': "Bearer " + self.authenticate()
        }

        try:
            if method == 'post':
                if json is None:
                    res = requests.post(url, headers=headers, params=params)
                else:
                    res = requests.post(url, headers=headers, params=params, json=json)
            elif method == 'get':
                    res = requests.get(url, headers=headers, params=params)

            print(url)
            print(headers)
            print(json)
            logger.info(res.status_code)
            return res.json()
        except Exception as e:
            logger.exception(e)
            return {}

    def create_order(self, data):
        uri = '/api/affiliate/SubmitOrder'

        return self._make_request_(uri, json=data, method='post')

    def order_status(self, AffiliateOrderNumber):
        uri = '/api/affiliate/GetOrderInfo/{}'.format(AffiliateOrderNumber)
        return self._make_request_(uri, method='get')

    def cancel_order(self, AffiliateOrderNumber):
        uri = '/api/affiliate/CancelOrder/{}'.format(AffiliateOrderNumber)
        return self._make_request_(uri, method='post')

    def search_process(self, data):
        uri = 'api/affiliate/SearchPrices'
        return self._make_request_(uri, json=data, method='post')

    def mark_order(self, AffiliateOrderNumber):
        uri = 'api/affiliate/MarkOrderStat/{}'.format(AffiliateOrderNumber)
        return self._make_request_(uri, method='post')

    def update_shipping(self, AffiliateOrderNumber, ShippingMethod):
        uri = 'api/affiliate/UpdateShipping/{0}/{1}'.format(AffiliateOrderNumber, ShippingMethod)
        return self._make_request_(uri, method='post')

    def order_note(self, AffiliateOrderNumber):
        uri = 'api/affiliate/AddOrderNote/{}'.format(AffiliateOrderNumber)
        return self._make_request_(uri, method='post')

    def update_order_status(self, AffiliateOrderNumber, OrderStatus):
        uri = 'api/affiliate/UpdateOrderStatus/{0}/{1}'.format(AffiliateOrderNumber, OrderStatus)
        return self._make_request_(uri, method='post')

    def update_orderitem_status(self, data):
        uri = 'api/affiliate/UpdateOrderItemStatus'.format(AffiliateOrderNumber, OrderStatus)
        return self._make_request_(uri, method='post')

gogomeds = GogoMedsAPI()

# if __name__ == '__main__':
#     data = {
#         'AffiliateOrderNumber' : "MJT-1530"
#     }
#     res = gogomeds.order_status(data)
#     print(res)
