from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.books.models import Book, Genre, UserFavoriteBook

User = get_user_model()


class GenreModelTest(TestCase):

    def test_create_genre(self):
        genre = Genre.objects.create(name="Fiction")
        self.assertEqual(str(genre), "Fiction")

    def test_genre_name_unique(self):
        Genre.objects.create(name="Fiction")
        with self.assertRaises(IntegrityError):
            Genre.objects.create(name="Fiction")


class BookModelTest(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="1984",
            summary="A dystopian novel.",
            isbn="9780451524935",
            publication_date=date(1949, 6, 8),
            genre=self.genre,
        )

    def test_create_book(self):
        self.assertEqual(str(self.book), "1984")
        self.assertEqual(self.book.genre, self.genre)

    def test_isbn_unique(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Another Book",
                summary="Some summary.",
                isbn="9780451524935",  # дубль
                publication_date=date(2000, 1, 1),
                genre=self.genre,
            )

    def test_isbn_invalid(self):
        book = Book(
            title="Bad ISBN",
            summary="Some summary.",
            isbn="123",  # невалидный
            publication_date=date(2000, 1, 1),
            genre=self.genre,
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_isbn_10_valid(self):
        book = Book(
            title="Old Book",
            summary="Some summary.",
            isbn="019853453X",  # ISBN-10 с X
            publication_date=date(1990, 1, 1),
            genre=self.genre,
        )
        try:
            book.full_clean()
        except ValidationError:
            self.fail("Valid ISBN-10 raised ValidationError")

    def test_isbn_13_valid(self):
        book = Book(
            title="New Book",
            summary="Some summary.",
            isbn="9780306406157",
            publication_date=date(2000, 1, 1),
            genre=self.genre,
        )
        try:
            book.full_clean()
        except ValidationError:
            self.fail("Valid ISBN-13 raised ValidationError")

    def test_created_at_auto(self):
        self.assertIsNotNone(self.book.created_at)

    def test_genre_protect_on_delete(self):
        with self.assertRaises(Exception):
            self.genre.delete()

    def test_authors_many_to_many(self):
        from django.conf import settings
        from django.apps import apps
        Author = apps.get_model(settings.AUTHOR_MODEL)
        author = Author.objects.create(
            first_name="George",
            last_name="Orwell",
            biography="English novelist and essayist.",
            date_of_birth=date(1903, 6, 25),
            date_of_death=date(1950, 1, 21),
        )
        self.book.authors.add(author)
        self.assertIn(author, self.book.authors.all())


class UserFavoriteBookModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Classic")
        self.book = Book.objects.create(
            title="War and Peace",
            summary="A novel about the French invasion of Russia.",
            isbn="9780140444179",
            publication_date=date(1869, 1, 1),
            genre=self.genre,
        )

    def test_create_favorite(self):
        favorite = UserFavoriteBook.objects.create(user=self.user, book=self.book)
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.book, self.book)
        self.assertIsNotNone(favorite.added_at)

    def test_str_representation(self):
        favorite = UserFavoriteBook.objects.create(user=self.user, book=self.book)
        self.assertIn(str(self.user.id), str(favorite))
        self.assertIn(str(self.book.id), str(favorite))

    def test_delete_user_cascades(self):
        UserFavoriteBook.objects.create(user=self.user, book=self.book)
        self.user.delete()
        self.assertFalse(UserFavoriteBook.objects.filter(book=self.book).exists())

    def test_delete_book_cascades(self):
        UserFavoriteBook.objects.create(user=self.user, book=self.book)
        # We'll bypass the protection genre by deleting it through a set of queries
        Book.objects.filter(id=self.book.id).delete()
        self.assertFalse(UserFavoriteBook.objects.filter(user=self.user).exists())
