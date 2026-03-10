from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.apps import apps
from django.conf import settings
from apps.books.models import Book, Genre, UserFavoriteBook

User = get_user_model()
Author = apps.get_model(settings.AUTHOR_MODEL)

BOOKS_URL = reverse("books")
BOOK_FAVORITES_URL = BOOKS_URL + "?favorites=true"


def book_detail_url(pk):
    return reverse("book", kwargs={"pk": pk})


def book_favorite_url(pk):
    return reverse("book-favorite", kwargs={"pk": pk})


class BaseBookTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Fiction")
        self.author = Author.objects.create(
            first_name="George",
            last_name="Orwell",
            biography="English novelist and essayist.",
            date_of_birth=date(1903, 6, 25),
            date_of_death=date(1950, 1, 21),
        )
        self.book = Book.objects.create(
            title="1984",
            summary="A dystopian novel.",
            isbn="9780451524935",
            publication_date=date(1949, 6, 8),
            genre=self.genre,
        )
        self.book.authors.add(self.author)

    def _auth(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "test@example.com", "password": "testpass123"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )


class BookListCreateAPIViewTest(BaseBookTestCase):

    def test_list_books_unauthenticated(self):
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_books_returns_results(self):
        self._auth()
        response = self.client.get(BOOKS_URL)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_create_book_authenticated(self):
        self._auth()
        data = {
            "title": "Animal Farm",
            "summary": "A political allegory.",
            "isbn": "9780451526342",
            "publication_date": "1945-08-17",
            "genre": "Classic",
            "author_ids": [self.author.id],
        }
        response = self.client.post(BOOKS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(isbn="9780451526342").exists())

    def test_create_book_creates_genre_if_not_exists(self):
        self._auth()
        data = {
            "title": "Brave New World",
            "summary": "A dystopian novel.",
            "isbn": "9780060850524",
            "publication_date": "1932-01-01",
            "genre": "New Genre",
            "author_ids": [self.author.id],
        }
        response = self.client.post(BOOKS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Genre.objects.filter(name="New Genre").exists())

    def test_create_book_unauthenticated(self):
        data = {
            "title": "Animal Farm",
            "summary": "A political allegory.",
            "isbn": "9780451526342",
            "publication_date": "1945-08-17",
            "genre": "Classic",
            "author_ids": [self.author.id],
        }
        response = self.client.post(BOOKS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_invalid_isbn(self):
        self._auth()
        data = {
            "title": "Bad Book",
            "summary": "Some summary.",
            "isbn": "123",
            "publication_date": "2000-01-01",
            "genre": "Fiction",
            "author_ids": [self.author.id],
        }
        response = self.client.post(BOOKS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_genre(self):
        self._auth()
        response = self.client.get(BOOKS_URL, {"genres": self.genre.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data["results"]:
            self.assertEqual(book["genre"], self.genre.name)

    def test_search_by_title(self):
        self._auth()
        response = self.client.get(BOOKS_URL, {"search": "1984"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [b["title"] for b in response.data["results"]]
        self.assertIn("1984", titles)

    def test_search_by_author_last_name(self):
        self._auth()
        response = self.client.get(BOOKS_URL, {"search": "Orwell"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)


class BookRetrieveUpdateDestroyAPIViewTest(BaseBookTestCase):

    def test_retrieve_book(self):
        self._auth()
        response = self.client.get(book_detail_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "1984")

    def test_retrieve_not_found(self):
        self._auth()
        response = self.client.get(book_detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_book_authenticated(self):
        self._auth()
        data = {
            "title": "1984 Updated",
            "summary": "A dystopian novel.",
            "isbn": "9780451524935",
            "publication_date": "1949-06-08",
            "genre": "Fiction",
            "author_ids": [self.author.id],
        }
        response = self.client.put(book_detail_url(self.book.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "1984 Updated")

    def test_partial_update_book(self):
        self._auth()
        response = self.client.patch(
            book_detail_url(self.book.pk),
            {"title": "1984 Patched"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "1984 Patched")

    def test_update_book_unauthenticated(self):
        response = self.client.put(
            book_detail_url(self.book.pk),
            {"title": "Hacked"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_authenticated(self):
        self._auth()
        response = self.client.delete(book_detail_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_delete_book_unauthenticated(self):
        response = self.client.delete(book_detail_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FavoriteBookAPIViewTest(BaseBookTestCase):

    def test_add_favorite_authenticated(self):
        self._auth()
        response = self.client.post(book_favorite_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserFavoriteBook.objects.filter(user=self.user, book=self.book).exists()
        )

    def test_add_favorite_twice_returns_200(self):
        self._auth()
        self.client.post(book_favorite_url(self.book.pk))
        response = self.client.post(book_favorite_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_favorite_unauthenticated(self):
        response = self.client.post(book_favorite_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_remove_favorite_authenticated(self):
        self._auth()
        UserFavoriteBook.objects.create(user=self.user, book=self.book)
        response = self.client.delete(book_favorite_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserFavoriteBook.objects.filter(user=self.user, book=self.book).exists()
        )

    def test_remove_favorite_not_in_favorites(self):
        self._auth()
        response = self.client.delete(book_favorite_url(self.book.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_favorites_authenticated(self):
        self._auth()
        response = self.client.get(BOOK_FAVORITES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_favorites_unauthenticated(self):
        response = self.client.get(BOOK_FAVORITES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
