from django.test import TestCase
from rest_framework import status

from authors.apps.articles.models import Tag

class ModelTestCase(TestCase):
    """
    This class defines the test suite for the tag model.
    """

    def test_model_can_create_a_taglist(self):
        """Test the tag model can create ataglist"""

        response = Tag.objects.create(
            tag = ["Django-rest", "Django-taggit"]
        )
        self.assertTrue(isinstance(response, Tag))

    def test_model_returns_readable_representation(self):
        """
        Test a readable string is returned for the model instance.
        """

        response = Tag.objects.create(
            tag = ["Django-rest", "Django-taggit"]
        )
        self.assertIn("Django-rest", str(response))
