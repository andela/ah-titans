"""
Module contains Models for article related tables
"""
from authors.apps.authentication.models import User
from authors.apps.core.models import TimestampModel
from authors.apps.profiles.models import Profile
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from notifications.signals import notify
from django.contrib.contenttypes.models import ContentType


class Article(TimestampModel):
    """
    Defines the articles table and functionality
    """
    title = models.CharField(db_index=True, max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    body = models.TextField()
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    dislikes = models.ManyToManyField(
        User, related_name='dislikes', blank=True)
    tags = models.ManyToManyField(
        'articles.Tag', related_name='articles'
    )

    def __str__(self):
        return self.title


class Comment(MPTTModel, TimestampModel):
    body = models.TextField()
    parent = TreeForeignKey('self', related_name='reply_set',
                            null=True, on_delete=models.CASCADE)

    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'profiles.Profile', related_name='comments', on_delete=models.CASCADE
    )


class Ratings(models.Model):
    """
    Defines the ratings fields for a rater
    """
    rater = models.ForeignKey(
        Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,  on_delete=models.CASCADE, related_name="rating")
    counter = models.IntegerField(default=0)
    stars = models.IntegerField(null=False)


class Tag(TimestampModel):
    """This class defines the tag model"""

    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return '{}'.format(self.tag)


# class Notification(models.Model):
#     unread = models.BooleanField(default=True, blank=False, db_index=True)
#     verb = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     actor_content_type = models.ForeignKey(
#         ContentType, related_name='notify_actor', on_delete=models.CASCADE)
#     emailed = models.BooleanField(default=False, db_index=True)
#     subscribed = models.BooleanField(default=True, db_index=True)


def pre_save_article_receiver(sender, instance, *args, **kwargs):
    """
    Method uses a signal to add slug to an article before saving it
    A slug will always be unique
    """
    if instance.slug:
        return instance
    slug = slugify(instance.title)
    num = 1
    unique_slug = slug
    # loops until a unique slug is generated
    while Article.objects.filter(slug=unique_slug).exists():
        unique_slug = "%s-%s" % (slug, num)
        num += 1

    instance.slug = unique_slug


# Called just before a save is made in the db
pre_save.connect(pre_save_article_receiver, sender=Article)


def notify_followers_new_article(sender, instance, created, **kwargs):
    """
    Notify followers of new article posted.
    """
    user = User.objects.get(pk=instance.author.id)
    rec = []
    for follower in user.profile.follower.all():
        rec.append(follower.user)
    notify.send(instance, recipient=rec, verb='was posted')


post_save.connect(notify_followers_new_article, sender=Article)


def notify_comments_favorited_articles(sender, instance, created, **kwargs):
    notify.send(instance, recipient=User.objects.all(),
                verb='was commented on')


post_save.connect(notify_comments_favorited_articles, sender=Comment)
