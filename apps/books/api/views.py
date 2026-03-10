from django.db import transaction
from django.db.models import F, Prefetch
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import UserRateThrottle

from apps.books.models import Book, get_author_model, UserFavoriteBook
from .filters import BookFilter
from .serializers import BookSerializer


# When updating or creating a book
#  a new genre may be created.
#  To ensure rollback and integrity,
#  we use an atomic transaction.
class BookListCreateAPIView(ListCreateAPIView):
    queryset = (
        Book.objects
        .only("id", "title", "isbn", "publication_date")
        .annotate(genre_name=F("genre__name"))
        .prefetch_related(Prefetch(
            "authors",
            queryset=get_author_model().objects.only("id", "first_name", "last_name").all()
        ))
        .all()
    )
    serializer_class = BookSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BookFilter
    throttle_classes = [UserRateThrottle]

    @transaction.atomic
    def perform_create(self, serializer):
        return super().perform_create(serializer)


class BookModelViewMixin:
    queryset = (
        Book.objects
        .select_related("genre")
        .prefetch_related(Prefetch(
            "authors",
            queryset=get_author_model().objects.only("id", "first_name", "last_name").all()
        ))
        .all()
    )
    serializer_class = BookSerializer
    pagination_class = PageNumberPagination


class BookRetrieveUpdateDestroyAPIView(BookModelViewMixin, RetrieveUpdateDestroyAPIView):
    @transaction.atomic
    def perform_update(self, serializer):
        return super().perform_update(serializer)


class FavoriteBookRetriveAPIView(BookModelViewMixin, DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method.lower() == "post":
            return qs  # open access to the entire queryset
        return qs.filter(user_favorites__user=self.request.user)

    def perform_destroy(self, instance):
        UserFavoriteBook.objects.filter(book=instance, user=self.request.user).delete()

    # add favorite book
    @extend_schema(
        request=None,
        responses={
            201: BookSerializer,
            200: BookSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        book = self.get_object()
        _, created = UserFavoriteBook.objects.get_or_create(book=book, user=request.user)
        serializer = self.get_serializer(instance=book)
        if not created:
            return Response(serializer.data, status=status.HTTP_200_OK)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
