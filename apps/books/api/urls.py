from django.urls import path

from .views import (
    BookListCreateAPIView,
    BookRetrieveUpdateDestroyAPIView,
    FavoriteBookRetriveAPIView
)

urlpatterns = [
    path("books/", BookListCreateAPIView.as_view(), name="books"),
    path("books/<int:pk>/", BookRetrieveUpdateDestroyAPIView.as_view(), name="book"),
    path("books/<int:pk>/favorite/", FavoriteBookRetriveAPIView.as_view(), name="book-favorite"),
]
