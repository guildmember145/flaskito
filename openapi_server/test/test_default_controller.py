import unittest

from flask import json

from openapi_server.models.bank_get_banks import BankGetBanks  # noqa: E501
from openapi_server.models.merchant_get_payment_methods import MerchantGetPaymentMethods  # noqa: E501
from openapi_server.models.payment_get_payment import PaymentGetPayment  # noqa: E501
from openapi_server.models.payment_post_payment import PaymentPostPayment  # noqa: E501
from openapi_server.models.payment_post_payment2 import PaymentPostPayment2  # noqa: E501
from openapi_server.models.payment_post_payment_refunds import PaymentPostPaymentRefunds  # noqa: E501
from openapi_server.models.predict_get_predict import PredictGetPredict  # noqa: E501
from openapi_server.models.receiver_post_receiver import ReceiverPostReceiver  # noqa: E501
from openapi_server.models.receiver_post_receiver2 import ReceiverPostReceiver2  # noqa: E501
from openapi_server.models.success import Success  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_delete_payment_by_id(self):
        """Test case for delete_payment_by_id

        Delete payment by Id
        """
        headers = { 
            'Accept': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/payments/{id}'.format(id='id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_banks(self):
        """Test case for get_banks

        Get banks
        """
        headers = { 
            'Accept': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/banks',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_merchant_payment_methods_by_id(self):
        """Test case for get_merchant_payment_methods_by_id

        Get payment methods
        """
        headers = { 
            'Accept': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/merchants/{id}/paymentMethods'.format(id=3.4),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_payment_by_id(self):
        """Test case for get_payment_by_id

        Get payment by Id
        """
        headers = { 
            'Accept': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/payments/{id}'.format(id='id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_predict(self):
        """Test case for get_predict

        Get payment prediction
        """
        query_string = [('payer_email', 'payer_email_example'),
                        ('bank_id', 'bank_id_example'),
                        ('amount', 'amount_example'),
                        ('currency', 'currency_example')]
        headers = { 
            'Accept': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/predict',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_payment(self):
        """Test case for post_payment

        Create payment
        """
        payment_post_payment = openapi_server.PaymentPostPayment()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/payments',
            method='POST',
            headers=headers,
            data=json.dumps(payment_post_payment),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_payment_confirm_by_id(self):
        """Test case for post_payment_confirm_by_id

        Confirm payment by Id
        """
        headers = { 
            'Accept': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/payments/{id}/confirm'.format(id='id_example'),
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_payment_refunds_by_id(self):
        """Test case for post_payment_refunds_by_id

        Refund payment by Id
        """
        payment_post_payment_refunds = openapi_server.PaymentPostPaymentRefunds()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/payments/{id}/refunds'.format(id='id_example'),
            method='POST',
            headers=headers,
            data=json.dumps(payment_post_payment_refunds),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_post_receiver(self):
        """Test case for post_receiver

        Post receiver
        """
        receiver_post_receiver = openapi_server.ReceiverPostReceiver()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Api-Key': 'special-key',
        }
        response = self.client.open(
            '/v3/receivers',
            method='POST',
            headers=headers,
            data=json.dumps(receiver_post_receiver),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
