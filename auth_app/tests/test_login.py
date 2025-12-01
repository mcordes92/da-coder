from rest_framework.test import APITestCase
from django.urls import reverse

class LoginTests(APITestCase):
    def test_login_success(self):
            """
            Erfolgreiches Login liefert Token und User-Infos zurück, Status 200
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
        Fehlerhaftes Login gibt Status 400 zurück
        """
        login_url = reverse('login')
        login_payload = {
            "username": "unknownUser",
            "password": "wrongPassword"
        }
        response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(response.status_code, 400)