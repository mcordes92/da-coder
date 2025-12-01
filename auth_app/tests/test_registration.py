from rest_framework.test import APITestCase
from django.urls import reverse

class RegistrationTests(APITestCase):
    
    def test_registration_success(self):
        """
        Erfolgreiche Registrierung liefert Token und User-Infos zurück, Status 201
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