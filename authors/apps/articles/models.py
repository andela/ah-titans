"""
Module contains Models for article related tables
"""
from authors.apps.authentication.models import User
from authors.apps.core.models import TimestampModel
from django.db import models
from django.core.validators import URLValidator
from django.db.models.signals import pre_save
from django.utils.text import slugify

class Article(TimestampModel):
    """
    Defines the articles table and functionality
    """
    title = models.CharField(db_index=True, max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    body = models.TextField()
    description = models.TextField()
    # ::TODO, implement authors once the profile feature is merged
    # author = models.ForeignKey(User, related_name='articles',
    # on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Image():
    """
    Defines images table which stores image URLS
    Has a `belongs to one` relationship with the Article class
    """
    article = models.ForeignKey(
        Article, related_name='images', on_delete=models.CASCADE)
    image_url = models.TextField(validators=[URLValidator()])


def pre_save_article_receiver(sender, instance, *args, **kwargs):
    """
    Method uses a signal to add slug to an article before saving it
    A slug will always be unique
    """
    slug = slugify(instance.title)

    #check if slug exists
    num = 1
    unique_slug = slug
    # loops until a unique slug is generated
    while Article.objects.filter(slug=unique_slug).exists():
        unique_slug = "%s-%s" %(slug, num)
        num += 1

    instance.slug = unique_slug

# called just before a save is made in the db
pre_save.connect(pre_save_article_receiver, sender=Article)
