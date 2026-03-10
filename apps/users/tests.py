from django.test import TestCase

from .models import CustomUser


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_username_field_is_email(self):
        self.assertEqual(CustomUser.USERNAME_FIELD, "email")

    def test_required_fields(self):
        self.assertIn("email", CustomUser.REQUIRED_FIELDS)

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("testpass123"))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_superuser_creation(self):
        admin = CustomUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_str_representation(self):
        self.assertEqual(str(self.user), "testuser")
    
    def test_same_cred_creation(self):
        user = CustomUser.objects.create_user(
            username="test2@example.com",
            email="test2@example.com",
            password="testpass123",
        )
        self.assertEqual(user.email, user.username)
