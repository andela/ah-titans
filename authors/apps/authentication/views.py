from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from rest_framework.decorators import api_view, permission_classes
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http.response import HttpResponse
from datetime import datetime, timedelta
from social_core.backends.utils import load_backends
from .verification import SendEmail, account_activation_token
from social_django.utils import psa
import jwt
from requests.exceptions import HTTPError
from django.conf import settings

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, SocialSerializer
)


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny, )
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # calls function that sends verification email once user is registered
        SendEmail().send_verification_email(user.get('email', None), request)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Activate(APIView):
    # Gets uidb64 and token from the send_verification_email function and
    # if valid, changes the status of user in is_verified to True and is_active
    # to True. The user is then redirected to a html page once the verification
    # link is clicked

    permission_classes = (AllowAny, )
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            return HttpResponse('Thank you for your email confirmation. Now you can login your account')
        else:
            return HttpResponse('Activation link is invalid!')


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.user.is_verified:
            user_data = request.data.get('user', {})

            serializer_data = {
                'username': user_data.get('username', request.user.username),
                'email': user_data.get('email', request.user.email),
                
                'profile': {
                    'bio': user_data.get('bio', request.user.profile.bio),
                    'interests': user_data.get('interests', 
                        request.user.profile.interests),
                    'image': user_data.get('image', request.user.profile.image)
                }
            }

            # Here is that serialize, validate, save pattern we talked about
            # before.
            serializer = self.serializer_class(
                request.user, data=serializer_data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        message = {"Error": "Email for this user is not verified"}
        return Response(message, status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
@psa('social:complete')
def exchange_token(request, backend):
    #access token from front-end used to get user information
    #and a new user created.If user already exists then token 
    #is given to the user.
    serializer = SocialSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        try:
            nfe = settings.NON_FIELD_ERRORS_KEY
        except AttributeError:
            nfe = 'non_field_errors'

        try:
            token = serializer.data.get("access_token")
         
            user = request.backend.do_auth(serializer.validated_data['access_token'])
        except HTTPError as e:
          
            return Response(
                {'errors': {
                    'token': 'Invalid token',
                    'detail': str(e),
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user:
            if user.is_active:
                dt = datetime.now() + timedelta(days=30)
                token = jwt.encode({
                    'id': user.pk,
                    'exp': int(dt.strftime('%s'))
                    }, settings.SECRET_KEY, algorithm='HS256')


                token = token.decode('utf-8')
                return Response({'token': token})
            else:
              
                return Response(
                    {'errors': {nfe: 'This user account is inactive'}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {'errors': {nfe: "Authentication Failed"}},
                status=status.HTTP_400_BAD_REQUEST,

            )


