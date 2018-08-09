from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ArticleViewSet, CommentsDestroyGetCreateAPIView,
                    CommentsListCreateAPIView, DislikesAPIView, LikesAPIView,
                    NotificationAPIView, CommentNotificationAPIView, RateAPIView, TagListAPIView)

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
]
