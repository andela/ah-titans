import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

#my local imports
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .exceptions import ProfileDoesNotExist


class ProfileRetrieveAPIView(RetrieveAPIView):
    """
    This class contains view to retrieve a profile instance.
    Any user is allowed to retrieve a profile
    """

    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related('user')

    def retrieve(self, request, username, *args, **kwargs):
        try:
            profile = self.queryset.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist(
                'A profile for user {} does not exist.'.format(username))

        serializer = self.serializer_class(profile,)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserFollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('A profile for user {} does not exist.'.format(username))

        if follower.pk is followed.pk:
            raise serializers.ValidationError('You can not unfollow yourself.')

        follower.unfollow(followed)

        serializer = self.serializer_class(followed, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('A profile for user {} does not exist.'.format(username))

        if follower.pk is followed.pk:
            raise serializers.ValidationError('You can not follow yourself.')

        follower.follow(followed)

        serializer = self.serializer_class(followed, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowingRetrieve(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    # serializer_class = FollowersSerializer

    def get(self, request):
        follows = request.user.profile.follows.all()
        if len(follows) == 0:
            return Response({"following": "You are following 0 users."},
                            status=status.HTTP_200_OK)
        list1 = []
        for user in follows:
            list1.append(user.user.username)
        return Response({"following": list1, "count": len(follows)},
                        status=status.HTTP_200_OK)


class FollowersRetrieve(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def get(self, request):
        followers = request.user.profile.follower.all()
        if len(followers) == 0:
            return Response({"followers": "You have 0 followers."},
                            status=status.HTTP_200_OK)
        list1 = []
        for person in followers:
            list1.append(person.user.username)

        return Response({"followers": list1, "count": len(followers)},
                        status=status.HTTP_200_OK)
