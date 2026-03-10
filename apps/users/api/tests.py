from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

REGISTER_URL = reverse("register")
DESTROY_URL = reverse("destroy")


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


class DestroyAccountAPIViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="todelete",
            email="delete@example.com",
            password="StrongPass123!",
        )
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": "delete@example.com", "password": "StrongPass123!"},
        )
        self.token = token_response.data["access"]

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_destroy_success(self):
        self._auth()
        response = self.client.delete(DESTROY_URL, {"password": "StrongPass123!"})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email="delete@example.com").exists())

    def test_destroy_wrong_password(self):
        self._auth()
        response = self.client.delete(DESTROY_URL, {"password": "WrongPass!"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(email="delete@example.com").exists())

    def test_destroy_unauthenticated(self):
        response = self.client.delete(DESTROY_URL, {"password": "StrongPass123!"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_missing_password(self):
        self._auth()
        response = self.client.delete(DESTROY_URL, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
