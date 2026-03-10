from django.urls import path

from .views import (
    AuthorListAPIView,
    AuthorRetriveUpdateDestroyAPIView,
)

urlpatterns = [
    path("authors/", AuthorListAPIView.as_view(), name="authors"),
    path("authors/<int:pk>/", AuthorRetriveUpdateDestroyAPIView.as_view(), name="author-detail"),
]
