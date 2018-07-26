from .models import Article
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .serializers import ArticleSeriaizer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ArticleView(APIView):
    lookup_field = 'slug'
    query_set = Article.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = ArticleSeriaizer

    def post(self, request):
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
