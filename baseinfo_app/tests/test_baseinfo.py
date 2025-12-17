from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from profile_app.models import Profile
from offer_app.models import Offer
from review_app.models import Reviews


class BaseInfoHappyPathTests(APITestCase):
    """
    Happy Path Tests für den /api/base-info/ Endpoint
    """

    def setUp(self):
        """
        Setup: Testdaten erstellen für aussagekräftige Statistiken
        """
        # Business User erstellen
        self.business_user1 = User.objects.create_user(
            username='business1',
            email='business1@example.com',
            password='testpass123'
        )
        self.business_user2 = User.objects.create_user(
            username='business2',
            email='business2@example.com',
            password='testpass123'
        )
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='testpass123'
        )
        
        # Business Profiles erstellen
        self.business_profile1 = Profile.objects.create(
            user=self.business_user1,
            type='business'
        )
        self.business_profile2 = Profile.objects.create(
            user=self.business_user2,
            type='business'
        )
        
        # Customer Profile erstellen (sollte nicht gezählt werden)
        self.customer_profile = Profile.objects.create(
            user=self.customer_user,
            type='customer'
        )
        
        # Offers erstellen
        self.offer1 = Offer.objects.create(
            user=self.business_user1,
            title='Test Offer 1',
            description='Description 1'
        )
        self.offer2 = Offer.objects.create(
            user=self.business_user2,
            title='Test Offer 2',
            description='Description 2'
        )
        self.offer3 = Offer.objects.create(
            user=self.business_user1,
            title='Test Offer 3',
            description='Description 3'
        )
        
        # Reviews erstellen
        self.review1 = Reviews.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user1,
            rating=5,
            description='Great service!'
        )
        self.review2 = Reviews.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user2,
            rating=4,
            description='Good service'
        )

    def test_get_base_info_success_with_data(self):
        """
        Status Code 200: Die Basisinformationen wurden erfolgreich abgerufen.
        Test mit vorhandenen Daten in der Datenbank.
        """
        url = reverse('baseinfo')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)
        
        # Prüfe die korrekten Werte
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['average_rating'], 4.5)  # (5 + 4) / 2
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertEqual(response.data['offer_count'], 3)

    def test_get_base_info_success_empty_database(self):
        """
        Status Code 200: Die Basisinformationen wurden erfolgreich abgerufen.
        Test mit leerer Datenbank (alle Werte sollten 0 sein).
        """
        # Lösche alle erstellten Objekte
        Reviews.objects.all().delete()
        Offer.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()
        
        url = reverse('baseinfo')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0)
        self.assertEqual(response.data['business_profile_count'], 0)
        self.assertEqual(response.data['offer_count'], 0)

    def test_get_base_info_no_authentication_required(self):
        """
        Status Code 200: Keine Authentifizierung erforderlich.
        No Permissions required - Endpoint sollte ohne Token erreichbar sein.
        """
        url = reverse('baseinfo')
        
        # Explizit ohne Authentifizierung
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)

    def test_get_base_info_with_authentication(self):
        """
        Status Code 200: Auch mit Authentifizierung funktioniert der Endpoint.
        """
        url = reverse('baseinfo')
        
        # Mit Authentifizierung
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('review_count', response.data)

    def test_get_base_info_only_business_profiles_counted(self):
        """
        Status Code 200: Nur Business-Profile werden gezählt, keine Customer-Profile.
        """
        url = reverse('baseinfo')
        
        # Erstelle zusätzliche Customer-Profile
        customer2 = User.objects.create_user(
            username='customer2',
            email='customer2@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=customer2, type='customer')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Sollte immer noch nur 2 Business-Profile zählen
        self.assertEqual(response.data['business_profile_count'], 2)

    def test_get_base_info_average_rating_calculation(self):
        """
        Status Code 200: Die durchschnittliche Bewertung wird korrekt berechnet.
        """
        # Füge weitere Reviews hinzu für verschiedene Ratings
        Reviews.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user1,
            rating=3,
            description='Average'
        )
        Reviews.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user2,
            rating=2,
            description='Below average'
        )
        
        url = reverse('baseinfo')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # (5 + 4 + 3 + 2) / 4 = 3.5
        self.assertEqual(response.data['average_rating'], 3.5)
        self.assertEqual(response.data['review_count'], 4)

    def test_get_base_info_response_structure(self):
        """
        Status Code 200: Die Response enthält alle erforderlichen Felder.
        """
        url = reverse('baseinfo')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Prüfe, dass genau die erwarteten Felder vorhanden sind
        expected_fields = {'review_count', 'average_rating', 'business_profile_count', 'offer_count'}
        self.assertEqual(set(response.data.keys()), expected_fields)
        
        # Prüfe Datentypen
        self.assertIsInstance(response.data['review_count'], int)
        self.assertIsInstance(response.data['business_profile_count'], int)
        self.assertIsInstance(response.data['offer_count'], int)
        self.assertIsInstance(response.data['average_rating'], (int, float))


class BaseInfoUnhappyPathTests(APITestCase):
    """
    Unhappy Path Tests für den /api/base-info/ Endpoint
    """

    def test_get_base_info_wrong_http_method_post(self):
        """
        Status Code 405: POST Methode ist nicht erlaubt.
        """
        url = reverse('baseinfo')
        
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, 405)

    def test_get_base_info_wrong_http_method_put(self):
        """
        Status Code 405: PUT Methode ist nicht erlaubt.
        """
        url = reverse('baseinfo')
        
        response = self.client.put(url, {})
        
        self.assertEqual(response.status_code, 405)

    def test_get_base_info_wrong_http_method_patch(self):
        """
        Status Code 405: PATCH Methode ist nicht erlaubt.
        """
        url = reverse('baseinfo')
        
        response = self.client.patch(url, {})
        
        self.assertEqual(response.status_code, 405)

    def test_get_base_info_wrong_http_method_delete(self):
        """
        Status Code 405: DELETE Methode ist nicht erlaubt.
        """
        url = reverse('baseinfo')
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 405)

   