from django.db import models
from django.core.validators import URLValidator
from authors.apps.core.models import TimestampModel
from authors.apps.authentication.models import User

class Article(TimestampModel):
    """
    Defines the articles table and functionality
    """
    title = models.CharField(db_index=True, max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    body = models.TextField()
    description = models.TextField()
    # ::TODO, implement authors once the profile feature is merged
    # author = models.ForeignKey(User, related_name='articles', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Image():
    """
    Defines images table which stores image URLS
    Has a `belongs to one` relationship with the Article class
    """
    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)
    image_url = models.TextField(validators=[URLValidator()])
