from rest_framework import serializers
from .models import Article


class ArticleSeriaizer(serializers.ModelSerializer):
    """
    Defines the article serializer

    """

    title = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    slug = serializers.SlugField(required=False)
    image_url = serializers.ImageField(required=False)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Article
        fields = ['title', 'slug', 'body',
                  'description', 'image_url', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Article.objects.create(**validated_data)
