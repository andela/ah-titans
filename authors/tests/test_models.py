from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from ..apps.authentication.models import User

class ModelTestCase(TestCase):
    """This class defines the test suite for the article model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.user = User.objects.create(username="nerd", email="nerd@nerd.com")

    def test_model_can_create_a_user(self):
        """Test the user model can create a user."""
        self.assertTrue(isinstance(self.user, User))

    def test_model_returns_readable_representation(self):
        """Test a readable string is returned for the model instance."""
        self.assertEqual(str(self.user), "nerd@nerd.com")
    