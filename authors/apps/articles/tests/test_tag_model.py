from django.test import TestCase
from rest_framework import status

from authors.apps.authentication.models import User
from authors.apps.articles import models

class CreateArticle():
    def __init__(self):
        self.title = "Django is life"
        self.body = """Try it today. Lorem ipsum dolor sit amet, 
                consectetur adipiscing elit, sed do eiusmod tempor 
                incididunt ut labore et dolore magna aliqua. Ut enim 
                ad minim veniam, quis nostrud exercitation ullamco laboris"""
        self.description = "Django"
        self.tagList = ["Django-rest", "Django-taggit"]

    def create_a_user(self, username="nerd", email="nerd@nerd.com", password="Secret123456"):
        """Creating a test user"""
        user = User.objects.create_user(username, email, password)
        user.save()
        return user

    def create_article(self):
        """Creating a test article with a taglist"""
        user = self.create_a_user()
        article = models.Article.objects.create(
            title=self.title,
            description=self.description,
            body=self.body,
            tagList=self.tagList,
            author=user.profile)
        article.save()
        return article


class ModelTestCase(TestCase):
    """
    This class defines the test suite for the tag model.
    """

    def test_model_can_create_a_taglist(self):
        """Test the tag model can create ataglist"""

        response = models.Tag.objects.create(
            tag=self.tagList
        )
        self.assertIn(list(response), ["Django-rest", "Django-taggit"])
