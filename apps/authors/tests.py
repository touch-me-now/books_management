from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.authors.models import Author


class AuthorModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Leo",
            last_name="Tolstoy",
            biography="Leo Tolstoy was a Russian novelist.",
            date_of_birth=date(1828, 9, 9),
            date_of_death=date(1910, 11, 20),
        )

    def test_create_author(self):
        self.assertEqual(self.author.first_name, "Leo")
        self.assertEqual(self.author.last_name, "Tolstoy")

    def test_str_representation(self):
        self.assertEqual(str(self.author), "L. Tolstoy")

    def test_get_short_name(self):
        self.assertEqual(self.author.get_short_name(), "L. Tolstoy")

    def test_date_of_death_optional(self):
        author = Author.objects.create(
            first_name="Haruki",
            last_name="Murakami",
            biography="Haruki Murakami is a Japanese novelist.",
            date_of_birth=date(1949, 1, 12),
            date_of_death=None,
        )
        self.assertIsNone(author.date_of_death)

    def test_unique_name_constraint(self):
        with self.assertRaises(IntegrityError):
            Author.objects.create(
                first_name="Leo",
                last_name="Tolstoy",
                biography="Another Leo Tolstoy.",
                date_of_birth=date(1900, 1, 1),
            )

    def test_birth_before_death_constraint(self):
        author = Author(
            first_name="Invalid",
            last_name="Author",
            biography="Some biography here.",
            date_of_birth=date(1950, 1, 1),
            date_of_death=date(1900, 1, 1),  # death earlier than birth
        )
        with self.assertRaises(ValidationError):
            author.full_clean()

    def test_biography_min_length(self):
        author = Author(
            first_name="John",
            last_name="Doe",
            biography="Short",  # less than 10 symbols
            date_of_birth=date(1990, 1, 1),
        )
        with self.assertRaises(ValidationError):
            author.full_clean()

    def test_same_birth_and_death_date_invalid(self):
        author = Author(
            first_name="Same",
            last_name="Date",
            biography="Some biography here.",
            date_of_birth=date(1900, 1, 1),
            date_of_death=date(1900, 1, 1),  # same dates
        )
        with self.assertRaises(ValidationError):
            author.full_clean()
