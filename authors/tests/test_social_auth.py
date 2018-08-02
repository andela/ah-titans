from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
import os

class ViewTestCase(TestCase):
    """Test suite for the api  social login api view."""

    def setUp(self):
        """Define the test client and other test variables."""

        client = APIClient()

class Testsocial(ViewTestCase, APITestCase):
    """This class defines the test suite all social auth."""
    
    def test_google(self):
        """
        Test login by google
        """
        access_token = os.environ.get("GoogleAccessToken")
        response = self.client.post('/api/users/auth/google-oauth2',
            data={'access_token':access_token})

      

        self.assertContains(response, "token")

        self.assertEqual(response.status_code, 200)


    def test_facebook(self):
        """
        Test login by facebook
        """
        access_token = os.environ.get("FbAccessToken", "none")
        response = self.client.post('/api/users/auth/facebook',
            data={'access_token':access_token})

        self.assertContains(response, "token")

        self.assertEqual(response.status_code, 200)


    def test_only_allowed_backends_work(self):
        """
        Test for yahoo for instance which is not defined at the moment
        """
        access_token = "EAAH9vlgjWYgBAJzlomW4fMBofoCKwZDZD"
        response = self.client.post('/api/users/auth/yahoo',
            data={'access_token':access_token})

        self.assertEqual(response.status_code, 404)

