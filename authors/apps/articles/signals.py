# from django.db.models.signals import post_save
# from notifications.signals import notify
#
# from .models import Article
#
#
# def notify_followers_new_article(sender, instance, created, **kwargs):
#     notify.send(instance, recipient=user, verb='was posted')
#
#
# post_save.connect(notify_followers_new_article, sender=Article)
