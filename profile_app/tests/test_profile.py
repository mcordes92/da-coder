from rest_framework.test import APITestCase
from django.urls import reverse

def registerUser(self):
    reg_url = reverse('registration')
    payload = {
        "username": "loginUser",
        "email": "login@mail.de",
        "password": "securePassword!",
        "repeated_password": "securePassword!",
        "type": "customer"
    }

    response = self.client.post(reg_url, payload, format='json')

    self.assertIn(response.status_code, [200, 201])
    token = response.data.get('token', None)
    self.assertIsNotNone(token)
    return token

class ProfileTests(APITestCase):

    def test_get_profile_success(self):
        """
        Erfolgreiches Abrufen des Profils liefert Status 200 zurück
        """

        token = registerUser(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        
        url = reverse('profileGetPatch', kwargs={'pk': 1})

        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        
        self.assertIn('user', response.data)
        self.assertIn('username', response.data)

        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)     
        self.assertIn('file', response.data)
        self.assertIn('location', response.data)
        self.assertIn('tel', response.data) 
        self.assertIn('description', response.data) 
        self.assertIn('working_hours', response.data) 

        types = ['customer', 'business']
        self.assertIn(response.data['type'], types)

        self.assertIn('email', response.data) 
        self.assertIn('created_at', response.data)

    def test_get_profile_unauthorized(self):
        """
        Abrufen des Profils ohne Authentifizierung liefert Status 401 zurück
        """
        url = reverse('profileGetPatch', kwargs={'pk': 1})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_get_profile_not_found(self):
        """
        Abrufen eines nicht existierenden Profils liefert Status 404 zurück
        """
        token = registerUser(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        
        url = reverse('profileGetPatch', kwargs={'pk': 9999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)

    def test_patch_profile_success(self):
        """
        Erfolgreiches Aktualisieren des Profils liefert Status 200 zurück
        """

        token = registerUser(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        url = reverse('profileGetPatch', kwargs={'pk': 1})

        payload = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Musterstadt",
            "tel": "0123456789",
            "description": "Ich bin ein Testbenutzer.",
            "working_hours": "9-17",
            "email": "max.mustermann@mail.de"
        }

        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 200)

        self.assertIn('user', response.data)
        self.assertIn('username', response.data)

        self.assertEqual(response.data['first_name'], payload['first_name'])
        self.assertEqual(response.data['last_name'], payload['last_name'])
        self.assertEqual(response.data['location'], payload['location'])
        self.assertEqual(response.data['tel'], payload['tel'])
        self.assertEqual(response.data['description'], payload['description'])
        self.assertEqual(response.data['working_hours'], payload['working_hours'])

        types = ['customer', 'business']
        self.assertIn(response.data['type'], types)

        self.assertEqual(response.data['email'], payload['email'])

        self.assertIn('created_at', response.data)

    def test_patch_profile_unauthorized(self):
        """
        Aktualisieren des Profils ohne Authentifizierung liefert Status 401 zurück
        """
        url = reverse('profileGetPatch', kwargs={'pk': 1})
        payload = {"first_name": "Max"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, 401)

    def test_patch_profile_forbidden(self):
        """
        Aktualisieren des Profils eines anderen Benutzers liefert Status 403 zurück
        """
        # Erstelle zwei Benutzer
        token1 = self._register_user_with_type("user1", "user1@mail.de", "customer")
        token2 = self._register_user_with_type("user2", "user2@mail.de", "customer")
        
        # Authentifiziere als user2, versuche user1's Profil zu ändern (pk=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token2)
        url = reverse('profileGetPatch', kwargs={'pk': 1})
        payload = {"first_name": "Hacker"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, 403)

    def test_patch_profile_not_found(self):
        """
        Aktualisieren eines nicht existierenden Profils liefert Status 404 zurück
        """
        token = registerUser(self)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        
        url = reverse('profileGetPatch', kwargs={'pk': 9999})
        payload = {"first_name": "Max"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, 404)

    def _register_user_with_type(self, username, email, type):
        req_url = reverse('registration')
        payLoad = {
            "username": username,
            "email": email,
            "password": "securePassword!",
            "repeated_password": "securePassword!",
            "type": type
        }

        response = self.client.post(req_url, payLoad, format='json')

        self.assertIn(response.status_code, [200, 201])
        token = response.data.get('token', None)
        self.assertIsNotNone(token)
        return token


    def test_profiles_list_business_and_customer(self):
        """
        Erfolgreiches Abrufen der Profil-Listen für Business- und Customer-Profile liefert Status 200 zurück
        """

        customer_token = self._register_user_with_type("customerUser", "customer@mail.com", "customer")
        business_token = self._register_user_with_type("businessUser", "business@mail.com", "business")

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + customer_token)

        url_business = reverse('profilesListBusiness')
        response_business = self.client.get(url_business, format='json')
        self.assertEqual(response_business.status_code, 200)
        self.assertEqual(len(response_business.data), 1)
        self.assertEqual(response_business.data[0]['username'], 'businessUser')
        self.assertEqual(response_business.data[0]['type'], 'business')
       
        url_customer = reverse('profilesListCustomer')
        response_customer = self.client.get(url_customer, format='json')
        self.assertEqual(response_customer.status_code, 200)
        self.assertEqual(len(response_customer.data), 1)
        self.assertEqual(response_customer.data[0]['username'], 'customerUser')
        self.assertEqual(response_customer.data[0]['type'], 'customer')

    def test_profiles_list_business_unauthorized(self):
        """
        Abrufen der Business-Profile ohne Authentifizierung liefert Status 401 zurück
        """
        url = reverse('profilesListBusiness')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_profiles_list_customer_unauthorized(self):
        """
        Abrufen der Customer-Profile ohne Authentifizierung liefert Status 401 zurück
        """
        url = reverse('profilesListCustomer')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)