from django.urls import path
from rest_framework import routers
from .views import (
<<<<<<< HEAD
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, Activate, ResetPassAPIView, Reset, PassResetAPIView
=======
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, Activate, ExchangeToken, ResetPassAPIView, Reset
>>>>>>> [Feature #159053958] A user can receive a reset password email
)
app_name = 'authentication'
urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(), name="register"),
    path('users/login/', LoginAPIView.as_view()),
    path('activate/<uidb64>/<token>/', Activate.as_view(), name="activate"),
<<<<<<< HEAD
    path('users/auth/<backend>', ExchangeToken.as_view()),
    path('users/reset_pass/', ResetPassAPIView.as_view()),
    path('reset/<uidb64>/<token>/', Reset.as_view(), name="reset"),
    path('users/pass_reset/', PassResetAPIView.as_view()),
=======
    path('users/auth/<backend>', ExchangeToken.as_view())

    path('users/reset_pass/', ResetPassAPIView.as_view()),
    path('reset/<uidb64>/<token>/', Reset.as_view(), name="reset"),
>>>>>>> [Feature #159053958] A user can receive a reset password email
]
