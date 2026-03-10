from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.authors.models import Author

User = get_user_model()

AUTHORS_URL = reverse("authors")


def author_detail_url(pk):
    return reverse("author-detail", kwargs={"pk": pk})


class BaseAuthorTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.author = Author.objects.create(
            first_name="Leo",
            last_name="Tolstoy",
            biography="Leo Tolstoy was a Russian novelist regarded as one of the greatest authors.",
            date_of_birth=date(1828, 9, 9),
            date_of_death=date(1910, 11, 20),
        )

    def _auth(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "test@example.com", "password": "testpass123"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )


class AuthorListCreateAPIViewTest(BaseAuthorTestCase):

    def test_list_authors_unauthenticated(self):
        response = self.client.get(AUTHORS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authors_returns_results(self):
        self._auth()
        response = self.client.get(AUTHORS_URL)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_create_author_authenticated(self):
        self._auth()
        data = {
            "first_name": "Fyodor",
            "last_name": "Dostoevsky",
            "biography": "Fyodor Dostoevsky was a Russian novelist.",
            "date_of_birth": "1821-11-11",
            "date_of_death": "1881-02-09",
        }
        response = self.client.post(AUTHORS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Author.objects.filter(last_name="Dostoevsky").exists())

    def test_create_author_unauthenticated(self):
        data = {
            "first_name": "Fyodor",
            "last_name": "Dostoevsky",
            "biography": "Fyodor Dostoevsky was a Russian novelist.",
            "date_of_birth": "1821-11-11",
        }
        response = self.client.post(AUTHORS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_author_duplicate_name(self):
        self._auth()
        data = {
            "first_name": "Leo",
            "last_name": "Tolstoy",
            "biography": "Another Leo Tolstoy biography.",
            "date_of_birth": "1900-01-01",
        }
        response = self.client.post(AUTHORS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_author_date_of_birth_in_future(self):
        self._auth()
        data = {
            "first_name": "Future",
            "last_name": "Author",
            "biography": "Some biography here.",
            "date_of_birth": "2099-01-01",
        }
        response = self.client.post(AUTHORS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_of_birth", response.data)

    def test_create_author_death_before_birth(self):
        self._auth()
        data = {
            "first_name": "Invalid",
            "last_name": "Author",
            "biography": "Some biography here.",
            "date_of_birth": "1950-01-01",
            "date_of_death": "1900-01-01",
        }
        response = self.client.post(AUTHORS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_of_birth", response.data)

    def test_create_author_without_date_of_death(self):
        self._auth()
        data = {
            "first_name": "Haruki",
            "last_name": "Murakami",
            "biography": "Haruki Murakami is a Japanese novelist.",
            "date_of_birth": "1949-01-12",
        }
        response = self.client.post(AUTHORS_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["date_of_death"])

    def test_search_by_first_name(self):
        self._auth()
        response = self.client.get(AUTHORS_URL, {"search": "Leo"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [a["first_name"] for a in response.data["results"]]
        self.assertIn("Leo", names)

    def test_search_by_last_name(self):
        self._auth()
        response = self.client.get(AUTHORS_URL, {"search": "Tolstoy"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_ordering_by_date_of_birth(self):
        Author.objects.create(
            first_name="Fyodor",
            last_name="Dostoevsky",
            biography="Russian novelist.",
            date_of_birth=date(1821, 11, 11),
            date_of_death=date(1881, 2, 9),
        )
        self._auth()
        response = self.client.get(AUTHORS_URL, {"ordering": "date_of_birth"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [a["date_of_birth"] for a in response.data["results"]]
        self.assertEqual(dates, sorted(dates))


class AuthorRetrieveUpdateDestroyAPIViewTest(BaseAuthorTestCase):

    def test_retrieve_author(self):
        self._auth()
        response = self.client.get(author_detail_url(self.author.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["last_name"], "Tolstoy")

    def test_retrieve_not_found(self):
        self._auth()
        response = self.client.get(author_detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_author_authenticated(self):
        self._auth()
        data = {
            "first_name": "Leo",
            "last_name": "Tolstoy",
            "biography": "Updated biography for Leo Tolstoy.",
            "date_of_birth": "1828-09-09",
            "date_of_death": "1910-11-20",
        }
        response = self.client.put(author_detail_url(self.author.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.biography, "Updated biography for Leo Tolstoy.")

    def test_partial_update_author(self):
        self._auth()
        response = self.client.patch(
            author_detail_url(self.author.pk),
            {"biography": "Partially updated biography."},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.biography, "Partially updated biography.")

    def test_update_author_unauthenticated(self):
        response = self.client.put(
            author_detail_url(self.author.pk),
            {"first_name": "Hacked"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_author_authenticated(self):
        self._auth()
        # author without books — can be deleted
        response = self.client.delete(author_detail_url(self.author.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(pk=self.author.pk).exists())

    def test_delete_author_unauthenticated(self):
        response = self.client.delete(author_detail_url(self.author.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorDeleteProtectionTest(TransactionTestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.author = Author.objects.create(
            first_name="Leo",
            last_name="Tolstoy",
            biography="Leo Tolstoy was a Russian novelist.",
            date_of_birth=date(1828, 9, 9),
            date_of_death=date(1910, 11, 20),
        )

    def _auth(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "test@example.com", "password": "testpass123"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}"
        )

    def test_delete_author_sole_author_of_book(self):
        from apps.books.models import Book, Genre
        self._auth()
        genre = Genre.objects.create(name="Fiction")
        book = Book.objects.create(
            title="War and Peace",
            summary="A novel about French invasion.",
            isbn="9780140444179",
            publication_date=date(1869, 1, 1),
            genre=genre,
        )
        book.authors.add(self.author)
        response = self.client.delete(author_detail_url(self.author.pk))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Author.objects.filter(pk=self.author.pk).exists())
