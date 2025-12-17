from rest_framework.test import APITestCase
from django.urls import reverse

class LoginTests(APITestCase):
    def test_login_success(self):
        """
        Status Code 200: Erfolgreiche Anmeldung.
        Authentifizierung liefert Token und Benutzerinformationen zurück.
        """
        reg_url = reverse('registration')
        payload = {
            "username": "loginUser",
            "email": "login@mail.de",
            "password": "securePassword!",
            "repeated_password": "securePassword!",
            "type": "customer"
        }
        self.client.post(reg_url, payload, format='json')

        login_url = reverse('login')
        login_payload = {
            "username": "loginUser",
            "password": "securePassword!"
        }
        response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        self.assertIn("user_id", response.data)

    def test_login_wrong_credentials(self):
        """
        Status Code 400: Ungültige Anfragedaten - falsche Anmeldedaten
        """
        login_url = reverse('login')
        login_payload = {
            "username": "unknownUser",
            "password": "wrongPassword"
        }
        response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_missing_username(self):
        """
        Status Code 400: Ungültige Anfragedaten - fehlendes username-Feld
        """
        login_url = reverse('login')
        login_payload = {
            "password": "somePassword"
        }
        response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_missing_password(self):
        """
        Status Code 400: Ungültige Anfragedaten - fehlendes password-Feld
        """
        login_url = reverse('login')
        login_payload = {
            "username": "someUser"
        }
        response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_wrong_password(self):
        """
        Status Code 400: Ungültige Anfragedaten - falsches Passwort für existierenden User
        """
        reg_url = reverse('registration')
        payload = {
            "username": "existingUser",
            "email": "existing@mail.de",
            "password": "correctPassword!",
            "repeated_password": "correctPassword!",
            "type": "customer"
        }
        self.client.post(reg_url, payload, format='json')
        
        login_url = reverse('login')
        login_payload = {
            "username": "existingUser",
            "password": "wrongPassword"
        }
        response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(response.status_code, 400)