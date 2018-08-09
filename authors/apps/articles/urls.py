from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ArticleViewSet, CommentsDestroyGetCreateAPIView,
                    CommentsListCreateAPIView, DislikesAPIView, LikesAPIView,
                    NotificationAPIView, CommentNotificationAPIView, RateAPIView,
                    TagListAPIView, Notifications, UnreadNotificationsList, mark_all_as_read,
                    mark_as_read, delete)

app_name = "articles"

router = DefaultRouter()
router.register('articles', ArticleViewSet, base_name='articles')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<slug>/rate/', RateAPIView.as_view()),
    path('articles/<article_slug>/comments/',
         CommentsListCreateAPIView.as_view()),
    path('articles/<article_slug>/comments/<comment_pk>/',
         CommentsDestroyGetCreateAPIView.as_view()),
    path('articles/<slug>/like/', LikesAPIView.as_view()),
    path('articles/<slug>/dislike/', DislikesAPIView.as_view()),
    path('tags/', TagListAPIView.as_view()),
    path('notifications/', NotificationAPIView.as_view()),
    path('comment/notifications/', CommentNotificationAPIView.as_view()),
    path('notifications/<uidb64>/<token>/',
         Notifications.as_view(), name="notifications"),
    path('notifications/unread/', UnreadNotificationsList.as_view(), name='unread'),
    path('notifications/mark-all-as-read/', mark_all_as_read,
         name='mark_all_as_read'),
    path('notifications/mark-as-read/<slug>/',
         mark_as_read, name='mark_as_read'),
    path('notifications/delete/<slug>/', delete, name='delete'),
    path('notifications/subscriptionOn/', subscription_on, name='subscription_on'),
    path('notifications/subscriptionOff/', subscription_off, name='subscription_off'),
]
