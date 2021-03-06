from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Avg, Count
from notifications.models import Notification
from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article, Comment, CommentEditHistory, Ratings, Tag, Bookmarks
from .renderers import (ArticleJSONRenderer, CommentEditHistoryJSONRenderer,
                        CommentJSONRenderer, CommentLikeJSONRenderer,
                        FavoriteJSONRenderer, NotificationJSONRenderer,
                        RatingJSONRenderer, BookmarkJSONRenderer)
from .serializers import (ArticleSerializer, CommentEditHistorySerializer,
                          CommentSerializer, NotificationSerializer,
                          RatingSerializer, TagSerializer,
                          UpdateCommentSerializer)


class LargeResultsSetPagination(PageNumberPagination):
    """
    Set pagination results settings
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class ArticleViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    lookup_field = 'slug'
    queryset = Article.objects.annotate(
        average_rating=Avg("rating__stars")
    )
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer
    pagination_class = LargeResultsSetPagination

    def create(self, request):
        """
        Overrides the create method to create a article
        """
        article = request.data.get('article', {})
        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        Overrides the list method to get all articles
        """
        queryset = Article.objects.all()
        serializer_context = {'request': request}
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )
        output = self.get_paginated_response(serializer.data)
        return output

    def retrieve(self, request, slug):
        """
        Override the retrieve method to get a article
        """
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug doesn't exist")

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context

        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        """
        Override the update method to update an article
        """
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug doesn't exist.")

        if not serializer_instance.author_id == request.user.profile.id:
            raise PermissionDenied(
                "You are not authorized to edit this article.")

        serializer_data = request.data.get('article', )

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context,
            data=serializer_data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug):
        """
        Override the destroy method to delete an article
        """
        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug doesn't exist")

        if article.author_id == request.user.profile.id:
            article.delete()
        else:
            raise PermissionDenied(
                "You are not authorized to delete this article.")

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = self.queryset

        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag=tag)

        return queryset


class RateAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (RatingJSONRenderer,)
    serializer_class = RatingSerializer

    def post(self, request, slug):
        """
        Method that posts users article ratings
        """
        rating = request.data.get("rate", {})
        serializer = self.serializer_class(data=rating)
        serializer.is_valid(raise_exception=True)
        rating = serializer.data.get('rating')
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        ratings = Ratings.objects.filter(rater=request.user.profile,
                                         article=article).first()
        if not ratings:
            ratings = Ratings(
                article=article,
                rater=request.user.profile,
                stars=rating)
            ratings.save()
            avg = Ratings.objects.filter(
                article=article).aggregate(Avg('stars'))
            return Response({
                "avg": avg
            }, status=status.HTTP_201_CREATED)

        if ratings.counter >= 5:
            raise PermissionDenied(
                "You are not allowed to rate this article more than 5 times."
            )

        ratings.counter += 1
        ratings.stars = rating
        ratings.save()
        avg = Ratings.objects.filter(article=article).aggregate(Avg('stars'))
        return Response({"avg": avg}, status=status.HTTP_201_CREATED)


class FavoriteAPIView(APIView):
    lookup_field = 'slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (FavoriteJSONRenderer,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def post(self, request, slug):
        """
        Method that favorites articles.
        """
        serializer_context = {'request': request}
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        request.user.profile.favorite(article)

        serializer = self.serializer_class(
            article,
            context=serializer_context
        )
        return Response(serializer.data,  status=status.HTTP_201_CREATED)

    def delete(self, request, slug):
        """
        Method that favorites articles.
        """
        serializer_context = {'request': request}
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        request.user.profile.unfavorite(article)

        serializer = self.serializer_class(
            article,
            context=serializer_context
        )

        return Response(serializer.data,  status=status.HTTP_200_OK)


class CommentsListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.root_nodes().select_related(
        'article', 'article__author', 'article__author__user',
        'author', 'author__user'
    )
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def filter_queryset(self, queryset):
        # The built-in list function calls `filter_queryset`. Since we only
        # want comments for a specific article, this is a good place to do
        # that filtering.
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}

        return queryset.filter(**filters)

    def create(self, request, article_slug=None):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentsDestroyGetCreateAPIView(
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
):
    lookup_url_kwarg = 'comment_pk'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def destroy(self, request, article_slug=None, comment_pk=None):
        try:
            comment = Comment.objects.get(pk=comment_pk,)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')

        comment.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def create(self, request,  article_slug=None, comment_pk=None):
        data = request.data.get('comment', None)
        context = {'author': request.user.profile}
        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')
        try:
            context['parent'] = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this id does not exists')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, article_slug=None,
               comment_pk=None, *args, **kwargs):
        serializer_class = UpdateCommentSerializer
        data = request.data.get('comment', None)
        try:
            comment = Comment.objects.get(pk=comment_pk,
                                          author=request.user.profile)
        except Comment.DoesNotExist:
            raise NotFound(
                'This comment does not exist for authenticated user.'
            )
        if comment.body != data.get('body'):
            CommentEditHistory.objects.create(
                body=comment.body,
                comment_id=comment.pk,
                updated_at=comment.updated_at
            )
            updated_comment = serializer_class.update(
                data=data,
                instance=comment
            )
            return Response(
                self.serializer_class(updated_comment).data,
                status=status.HTTP_200_OK
            )
        return Response(
            self.serializer_class(comment).data,
            status=status.HTTP_200_OK
        )


class CommentEditHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    renderer_classes = [CommentEditHistoryJSONRenderer, ]
    serializer_class = CommentEditHistorySerializer
    queryset = CommentEditHistory.objects.all()

    def list(self, request, slug, comment_pk, *args, **kwargs):
        try:
            Comment.objects.get(pk=comment_pk, author=request.user.profile)
            serializer_instance = self.queryset.filter(comment_id=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound
        serializer = self.serializer_class(serializer_instance, many=True)

        return Response(serializer.data, status.HTTP_200_OK)


class LikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def put(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        if serializer_instance in Article.objects.filter(
                dislikes=request.user):
            serializer_instance.dislikes.remove(request.user)

        if serializer_instance in Article.objects.filter(
                likes=request.user):
            serializer_instance.likes.remove(request.user)
        else:
            serializer_instance.likes.add(request.user)

        serializer = self.serializer_class(serializer_instance,
                                           context=serializer_context,
                                           partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DislikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def put(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        if serializer_instance in Article.objects.filter(likes=request.user):
            serializer_instance.likes.remove(request.user)

        if serializer_instance in Article.objects.filter(
                dislikes=request.user):
            serializer_instance.dislikes.remove(request.user)
        else:
            serializer_instance.dislikes.add(request.user)

        serializer = self.serializer_class(serializer_instance,
                                           context=serializer_context,
                                           partial=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)


class NotificationViewset(mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = NotificationSerializer
    renderer_classes = (NotificationJSONRenderer, )

    def list(self, request):
        unread_count = request.user.notifications.unread().count()
        read_count = request.user.notifications.read().count()
        unread_serializer = self.serializer_class(
            data=request.user.notifications.unread(), many=True)
        unread_serializer.is_valid()
        read_serializer = self.serializer_class(
            data=request.user.notifications.read(), many=True)
        read_serializer.is_valid()
        request.user.notifications.mark_as_sent()
        return Response({'unread_count': unread_count, 'read_count': read_count,
                         'unread_list': unread_serializer.data, 'read_list': read_serializer.data},
                        status=status.HTTP_200_OK)

    def update(self, request, id):
        try:
            instance_data = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            raise NotFound("The notification with the given id doesn't exist")

        instance_data.mark_as_read()

        return Response("Notification marked as read", status=status.HTTP_200_OK)

    def delete(self, request, id):
        try:
            notification = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            raise NotFound("The notification with the given id doesn't exist")

        notification.delete()

        return Response({"Message": "Notification has been deleted"}, status=status.HTTP_200_OK)


class ReadAllNotificationViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    def update(self, request):
        try:
            instance_data = Notification.objects.filter(unread=True).all()
            if len(instance_data) < 1:
                raise ValueError
        except ValueError:
            raise NotFound("You have no unread notifications")

        instance_data.mark_all_as_read()

        return Response({"Message": "You have marked all notifications as read"},
                        status=status.HTTP_200_OK)


class FilterAPIView(generics.ListAPIView):

    model = Article
    queryset = Article.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer
    context_object_name = 'articles'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_kwargs = {}
        search_settings = getattr(settings, 'ARTICLE_SEARCH_SETTINGS', {})
        if 'config' in search_settings:
            self.config_kwargs['config'] = search_settings['config']

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get('title', None)
        if title is not None:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity('title', title),
            ).filter(similarity__gt=0.3).order_by('-similarity')
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity(
                    'author__user__username', author),
            ).filter(similarity__gt=0.3).order_by('-similarity')
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity(
                    'tags__tag', tag),
            ).filter(similarity__gt=0.3).order_by('-similarity')
        return queryset.order_by('created_at')


class LikeCommentLikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (CommentLikeJSONRenderer, )
    serializer_class = CommentSerializer

    def post(self, request,  article_slug=None, comment_pk=None):
        serializer_context = {'request': request}
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        try:
            serializer_instance = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this id does not exist')

        if serializer_instance in Comment.objects.filter(
                comment_likes=request.user):
            serializer_instance.comment_likes.remove(request.user)
        else:
            serializer_instance.comment_likes.add(request.user)

        if serializer_instance in Comment.objects.filter(
                comment_dislikes=request.user):
            serializer_instance.comment_dislikes.remove(request.user)
            serializer_instance.comment_likes.add(request.user)

        serializer = self.serializer_class(serializer_instance,
                                           context=serializer_context,
                                           partial=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DislikeCommentLikesAPIView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    renderer_classes = (CommentLikeJSONRenderer, )
    serializer_class = CommentSerializer

    def post(self, request,  article_slug=None, comment_pk=None):
        serializer_context = {'request': request}
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        try:
            serializer_instance = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this id does not exists')

        if serializer_instance in Comment.objects.filter(
                comment_dislikes=request.user):
            serializer_instance.comment_dislikes.remove(request.user)
        else:
            serializer_instance.comment_dislikes.add(request.user)

        if serializer_instance in Comment.objects.filter(
                comment_likes=request.user):
            serializer_instance.comment_likes.remove(request.user)
            serializer_instance.comment_dislikes.add(request.user)

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context,
            partial=True
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookmarkAPIView(APIView):
    lookup_field = 'slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (BookmarkJSONRenderer,)
    serializer_class = ArticleSerializer

    def post(self, request, slug):
        """
        Method that add article to bookmarked ones
        """
        serializer_context = {'request': request}
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")
        bookmark = Bookmarks.objects.filter(
            user=request.user.profile, article=article).first()
        if not bookmark:
            bookmarks = Bookmarks(article=article, user=request.user.profile)
            bookmarks.save()
            serializer = self.serializer_class(
                article,
                context=serializer_context
            )
            return Response(serializer.data,  status=status.HTTP_201_CREATED)
        return Response({
            "msg": "Article with the slug '{}' is already in bookmarks".format(slug)
        }, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, slug):
        """
        Method that removes article from the bookmarked ones
        """
        serializer_context = {'request': request}
        try:
            article = Article.objects.get(slug=slug).id
        except Article.DoesNotExist:
            raise NotFound("An article with this slug does not exist")

        try:
            bookmarked_article = Bookmarks.objects.get(article=article)
        except Bookmarks.DoesNotExist:
            raise NotFound("This article has not been bookmarked")

        bookmarked_article.delete()

        return Response({
            "msg": "Article with the slug '{}' has been removed from bookmarks".format(slug)
        }, status=status.HTTP_200_OK)
