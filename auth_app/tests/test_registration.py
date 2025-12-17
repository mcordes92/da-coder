from rest_framework.test import APITestCase
from django.urls import reverse

class RegistrationTests(APITestCase):
    
    def test_registration_success(self):
        """
        Status Code 201: Der Benutzer wurde erfolgreich erstellt.
        Erfolgreiche Registrierung liefert Token und User-Infos zurück.
        """
                
        url = reverse('registration')
       
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "repeated_password": "strongpassword123",
            "type": "customer"
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, 201)
        
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], payload['username'])
        self.assertEqual(response.data['email'], payload['email'])
        self.assertIn('user_id', response.data)

    def test_registration_missing_username(self):
        """
        Status Code 400: Ungültige Anfragedaten - fehlendes username-Feld
        """
        url = reverse('registration')
        payload = {
            "email": "test@example.com",
            "password": "strongpassword123",
            "repeated_password": "strongpassword123",
            "type": "customer"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_missing_email(self):
        """
        Status Code 400: Ungültige Anfragedaten - fehlende E-Mail
        """
        url = reverse('registration')
        payload = {
            "username": "testuser",
            "password": "strongpassword123",
            "repeated_password": "strongpassword123",
            "type": "customer"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_password_mismatch(self):
        """
        Status Code 400: Ungültige Anfragedaten - Passwörter stimmen nicht überein
        """
        url = reverse('registration')
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123",
            "repeated_password": "differentpassword",
            "type": "customer"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_duplicate_username(self):
        """
        Status Code 400: Ungültige Anfragedaten - Benutzername bereits vorhanden
        """
        url = reverse('registration')
        payload = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "strongpassword123",
            "repeated_password": "strongpassword123",
            "type": "customer"
        }
        self.client.post(url, payload, format='json')
        
        payload["email"] = "user2@example.com"
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_invalid_email(self):
        """
        Status Code 400: Ungültige Anfragedaten - ungültiges E-Mail-Format
        """
        url = reverse('registration')
        payload = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "strongpassword123",
            "repeated_password": "strongpassword123",
            "type": "customer"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)