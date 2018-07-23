from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from authors.apps.authentication.models import User

class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""

        self.user_data = {
            "username":"nerd",
            "email":"nerd@nerd.com",
            "password":"secret"
            }

        # Initialize client
        self.client = APIClient()

    def test_api_can_create_a_user(self):
        """Test the api can succefully create a user."""

        response = self.client.post(
            '/api/users/',
            self.user_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_can_login_a_user(self):
        """Test the api can succefuly login a user."""

        login_data = {
            "email":"nerd@nerd.com",
            "password":"secret"
            }
        self.client.post(
            '/api/users/',
            self.user_data
        )
        response = self.client.post(
            '/api/users/login',
            login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_login_with_wrong_password(self):
        """Test the api cannot login a user with a wrong password."""

        login_data = {
            "email":"nerd@nerd.com",
            "password":"wrong"
            }
        self.client.post(
            '/api/users/',
            self.user_data
        )
        response = self.client.post(
            '/api/users/login',
            login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_login_with_wrong_email(self):
        """Test the api cannot login a user with a wrong email."""

        login_data = {
            "email":"wrong@nerd.com",
            "password":"secret"
            }
        self.client.post(
            '/api/users/',
            self.user_data
        )
        response = self.client.post(
            '/api/users/login',
            login_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
