from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle

from apps.authors.models import Author
from .serializers import AuthorSerializer


class AuthorListAPIView(ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("first_name", "last_name")
    ordering_fields = ("date_of_birth", "date_of_death")
    throttle_classes = [UserRateThrottle]


class AuthorRetriveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def perform_destroy(self, instance):
        try:
            return super().perform_destroy(instance)
        except ProtectedError as e:
            raise ValidationError({"detail": e.args[0]})
    