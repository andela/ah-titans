from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, RateAPIView, CommentsListCreateAPIView,CommentsDestroyGetCreateAPIView

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
]
