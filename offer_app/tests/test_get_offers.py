from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from django.urls import reverse

class GetOffersTests(APITestCase):
    
    def test_get_offers_success(self):
        """
        Erfolgreiches Abrufen von Angeboten liefert eine Liste von Angeboten zurück, Status 200
        """
                
        url = reverse('offers-list')
       
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        
class PostOfferTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='strongpassword123')
        self.client.force_authenticate(user=self.user)

    def test_post_offer_success(self):
        """
        Erfolgreiches Erstellen eines Angebots liefert Status 201
        """

        url = reverse('offers-list')

        payload = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                "title": "Basic Design",
                "revisions": 2,
                "delivery_time_in_days": 5,
                "price": 100,
                "features": [
                    "Logo Design",
                    "Visitenkarte"
                ],
                "offer_type": "basic"
                },
                {
                "title": "Standard Design",
                "revisions": 5,
                "delivery_time_in_days": 7,
                "price": 200,
                "features": [
                    "Logo Design",
                    "Visitenkarte",
                    "Briefpapier"
                ],
                "offer_type": "standard"
                },
                {
                "title": "Premium Design",
                "revisions": 10,
                "delivery_time_in_days": 10,
                "price": 500,
                "features": [
                    "Logo Design",
                    "Visitenkarte",
                    "Briefpapier",
                    "Flyer"
                ],
                "offer_type": "premium"
                }
            ]
            }
        

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, 201)

        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertEqual(len(response.data['details']), 3)