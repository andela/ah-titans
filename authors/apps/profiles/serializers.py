from rest_framework import serializers

#my local imports
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """This class contains a serializer for the Profile model"""

    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField()
    following = serializers.BooleanField(default=False)

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'following')
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image
        else:
            return 'https://static.productionready.io/images/smiley-cyrus.jpg'
