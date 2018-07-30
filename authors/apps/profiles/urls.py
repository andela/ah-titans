from django.conf.urls import url

#my local imports
from .views import ProfileRetrieveAPIView

app_name = 'profiles'

urlpatterns = [
    url(r'^profiles/(?P<username>\w+)/?$',
        ProfileRetrieveAPIView.as_view()),
]
