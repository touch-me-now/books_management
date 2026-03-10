from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

REGISTER_URL = reverse("register")


class RegistrationAPIViewTest(APITestCase):

    def test_register_success(self):
        data = {"email": "newuser@example.com", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(username="existing", email="dup@example.com", password="pass")
        data = {"email": "dup@example.com", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_weak_password(self):
        data = {"email": "weak@example.com", "password": "123"}
        response = self.client.post(REGISTER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        data = {"email": "nopwd@example.com"}
        response = self.client.post(REGISTER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        data = {"email": "not-an-email", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_no_auth_required(self):
        self.client.credentials()
        data = {"email": "noauth@example.com", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, data)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
