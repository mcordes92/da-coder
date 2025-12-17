from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from profile_app.models import Profile
from offer_app.models import Offer, OfferDetail


# ============================================
# HAPPY PATH TESTS
# ============================================

class GetOffersListHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Abrufen der Angebotsliste"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Angebote erstellen
        self.offer1 = Offer.objects.create(
            user=self.business_user,
            title="Webentwicklung",
            description="Professionelle Webentwicklung"
        )
        OfferDetail.objects.create(
            offer=self.offer1,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
    
    def test_get_offers_list_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können die Angebotsliste abrufen (AllowAny)
        """
        url = reverse('offers-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_get_offers_list_authenticated(self):
        """
        Authentifizierte Benutzer können die Angebotsliste abrufen (Status 200)
        """
        customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=customer_user, type='customer')
        self.client.force_authenticate(user=customer_user)
        
        url = reverse('offers-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)


class GetOfferDetailHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Abrufen eines einzelnen Angebots"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        # Angebot erstellen
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Grafikdesign",
            description="Professionelles Grafikdesign"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo Design"],
            offer_type="basic"
        )
    
    def test_get_offer_detail_authenticated(self):
        """
        Authentifizierte Benutzer können ein einzelnes Angebot abrufen (Status 200)
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.offer.title)
        self.assertEqual(response.data['id'], self.offer.id)


class PostOfferHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Erstellen von Angeboten"""

    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='businessuser', password='strongpassword123')
        Profile.objects.create(user=self.business_user, type='business')
        self.client.force_authenticate(user=self.business_user)
        
        self.payload = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"],
                    "offer_type": "premium"
                }
            ]
        }

    def test_post_offer_as_business_user(self):
        """
        Business User können erfolgreich ein Angebot erstellen (Status 201)
        """
        url = reverse('offers-list')
        response = self.client.post(url, self.payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], self.payload['title'])
        self.assertEqual(len(response.data['details']), 3)
        self.assertEqual(response.data['user'], self.business_user.id)


class UpdateOfferHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Aktualisieren von Angeboten"""
    
    def setUp(self):
        # Business User und Angebot erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Original Title",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
        
        self.client.force_authenticate(user=self.business_user)
    
    def test_update_offer_as_owner(self):
        """
        Besitzer können ihr eigenes Angebot aktualisieren (Status 200)
        """
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        payload = {"title": "Updated Title"}
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Updated Title")
        
        # Datenbank überprüfen
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Updated Title")


class DeleteOfferHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Löschen von Angeboten"""
    
    def setUp(self):
        # Business User und Angebot erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="To Delete",
            description="Will be deleted"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
        
        self.client.force_authenticate(user=self.business_user)
    
    def test_delete_offer_as_owner(self):
        """
        Besitzer können ihr eigenes Angebot löschen (Status 204)
        """
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        
        # Überprüfen, dass das Angebot gelöscht wurde
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())


class GetOfferDetailViewHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Abrufen von Angebotsdetails über OfferDetailsView"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        # Angebot und Details erstellen
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Premium Package",
            revisions=5,
            delivery_time_in_days=10,
            price=500,
            features=["Feature A", "Feature B"],
            offer_type="premium"
        )
    
    def test_get_offer_detail_authenticated(self):
        """
        Authentifizierte Benutzer können Angebotsdetails abrufen (Status 200)
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offer-details', kwargs={'pk': self.offer_detail.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Premium Package")
        self.assertEqual(response.data['price'], 500)


# ============================================
# UNHAPPY PATH TESTS
# ============================================

class GetOfferDetailUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene Retrieve-Requests"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
    
    def test_get_offer_detail_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können kein einzelnes Angebot abrufen (401)
        """
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 401)
    
    def test_get_nonexistent_offer(self):
        """
        Abrufen eines nicht existierenden Angebots gibt Status 404 zurück
        """
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 404)


class PostOfferUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene Post-Requests"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='businessuser', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(username='customeruser', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        self.payload = {
            "title": "Test Offer",
            "description": "Test Description",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }
    
    def test_post_offer_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können kein Angebot erstellen (401)
        """
        url = reverse('offers-list')
        response = self.client.post(url, self.payload, format='json')

        self.assertEqual(response.status_code, 401)
    
    def test_post_offer_as_customer_user(self):
        """
        Customer User können kein Angebot erstellen (403) - nur Business User
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-list')
        response = self.client.post(url, self.payload, format='json')

        self.assertEqual(response.status_code, 403)
    
    def test_post_offer_with_invalid_data(self):
        """
        Angebot mit ungültigen Daten kann nicht erstellt werden (400)
        """
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offers-list')
        
        invalid_payload = {
            "title": "",  # Leerer Titel
            "description": "Test"
        }
        response = self.client.post(url, invalid_payload, format='json')

        self.assertEqual(response.status_code, 400)


class UpdateOfferUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene Update-Requests"""
    
    def setUp(self):
        # Business User 1
        self.business_user1 = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user1, type='business')
        
        # Business User 2
        self.business_user2 = User.objects.create_user(username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')
        
        # Customer User
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        # Angebot von Business User 1
        self.offer = Offer.objects.create(
            user=self.business_user1,
            title="Original Title",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
    
    def test_update_offer_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können kein Angebot aktualisieren (401)
        """
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        payload = {"title": "Updated Title"}
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 401)
    
    def test_update_offer_as_non_owner(self):
        """
        Benutzer können Angebote anderer Benutzer nicht aktualisieren (403)
        """
        self.client.force_authenticate(user=self.business_user2)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        payload = {"title": "Hacked Title"}
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 403)
        
        # Überprüfen, dass nichts geändert wurde
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Original Title")
    
    def test_update_offer_as_customer(self):
        """
        Customer User können keine Angebote aktualisieren (Status 403)
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        payload = {"title": "Customer Update"}
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 403)
    
    def test_update_offer_with_invalid_data(self):
        """
        Update mit ungültigen Daten schlägt fehl (Status 400)
        """
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        payload = {"title": ""}  # Leerer Titel ist ungültig
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 400)
    
    def test_update_nonexistent_offer(self):
        """
        Update eines nicht existierenden Angebots gibt Status 404 zurück
        """
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('offers-detail', kwargs={'pk': 99999})
        payload = {"title": "Updated Title"}
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, 404)


class DeleteOfferUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene Delete-Requests"""
    
    def setUp(self):
        # Business User 1
        self.business_user1 = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user1, type='business')
        
        # Business User 2
        self.business_user2 = User.objects.create_user(username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')
        
        # Customer User
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        # Angebot von Business User 1
        self.offer = Offer.objects.create(
            user=self.business_user1,
            title="To Delete",
            description="Test"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
    
    def test_delete_offer_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können kein Angebot löschen (401)
        """
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 401)
        
        # Überprüfen, dass das Angebot noch existiert
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())
    
    def test_delete_offer_as_non_owner(self):
        """
        Benutzer können Angebote anderer Benutzer nicht löschen (403)
        """
        self.client.force_authenticate(user=self.business_user2)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)
        
        # Überprüfen, dass das Angebot noch existiert
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())
    
    def test_delete_offer_as_customer(self):
        """
        Customer User können keine Angebote löschen (403)
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('offers-detail', kwargs={'pk': self.offer.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 403)
        
        # Überprüfen, dass das Angebot noch existiert
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())
    
    def test_delete_nonexistent_offer(self):
        """
        Löschen eines nicht existierenden Angebots gibt Status 404 zurück
        """
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('offers-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 404)


class GetOfferDetailViewUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene Requests an OfferDetailsView"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Angebot und Details erstellen
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
    
    def test_get_offer_detail_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können keine Angebotsdetails abrufen (401)
        """
        url = reverse('offer-details', kwargs={'pk': self.offer_detail.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 401)
    
    def test_get_nonexistent_offer_detail(self):
        """
        Abrufen nicht existierender Angebotsdetails gibt Status 404 zurück
        """
        self.client.force_authenticate(user=self.business_user)
        url = reverse('offer-details', kwargs={'pk': 99999})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, 404)


# ============================================
# VALIDATION & EDGE CASE TESTS
# ============================================

class OfferValidationTests(APITestCase):
    """Tests für Validierungslogik im Serializer"""
    
    def setUp(self):
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        self.client.force_authenticate(user=self.business_user)
    
    def test_create_offer_with_less_than_3_details(self):
        """
        Angebot mit weniger als 3 Details schlägt fehl (Status 400)
        """
        url = reverse('offers-list')
        payload = {
            "title": "Test Offer",
            "description": "Test Description",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('details', response.data)
    
    def test_create_offer_with_duplicate_offer_types(self):
        """
        Angebot mit duplizierten offer_types schlägt fehl (Status 400)
        """
        url = reverse('offers-list')
        payload = {
            "title": "Test Offer",
            "description": "Test Description",
            "details": [
                {
                    "title": "Basic 1",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                },
                {
                    "title": "Basic 2",
                    "revisions": 3,
                    "delivery_time_in_days": 7,
                    "price": 150,
                    "features": ["Feature 2"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 5,
                    "delivery_time_in_days": 10,
                    "price": 200,
                    "features": ["Feature 3"],
                    "offer_type": "standard"
                }
            ]
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('details', response.data)
    
    def test_update_offer_with_details(self):
        """
        Angebot-Details können via PATCH aktualisiert werden
        """
        # Angebot erstellen
        offer = Offer.objects.create(
            user=self.business_user,
            title="Original Title",
            description="Original Description"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic Original",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Standard Original",
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=["Feature 2"],
            offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Premium Original",
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=["Feature 3"],
            offer_type="premium"
        )
        
        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        payload = {
            "title": "Updated Title",
            "details": [
                {
                    "offer_type": "basic",
                    "title": "Basic Updated",
                    "price": 150
                }
            ]
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, 200)
        
        # Überprüfen, dass das Detail aktualisiert wurde
        basic_detail = OfferDetail.objects.get(offer=offer, offer_type='basic')
        self.assertEqual(basic_detail.title, "Basic Updated")
        self.assertEqual(basic_detail.price, 150)
    
    def test_update_offer_detail_without_offer_type(self):
        """
        Update von Details ohne offer_type schlägt fehl (Status 400)
        """
        offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
        
        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        payload = {
            "details": [
                {
                    "title": "Updated without type",
                    "price": 150
                }
            ]
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_offer_detail_with_nonexistent_offer_type(self):
        """
        Update eines nicht existierenden offer_types schlägt fehl (Status 400)
        """
        offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        OfferDetail.objects.create(
            offer=offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
        
        url = reverse('offers-detail', kwargs={'pk': offer.pk})
        payload = {
            "details": [
                {
                    "offer_type": "premium",  # Existiert nicht für dieses Angebot
                    "title": "Premium Update",
                    "price": 500
                }
            ]
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, 400)


class OfferModelMethodTests(APITestCase):
    """Tests für Model-Methoden und Serializer-Methoden"""
    
    def setUp(self):
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business', first_name='Max', last_name='Mustermann')
        self.client.force_authenticate(user=self.business_user)
        
        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Test Offer",
            description="Test Description"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature 1"],
            offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Standard",
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=["Feature 2"],
            offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=self.offer,
            title="Premium",
            revisions=10,
            delivery_time_in_days=3,  # Kürzeste Lieferzeit
            price=50,  # Niedrigster Preis
            features=["Feature 3"],
            offer_type="premium"
        )
    
    def test_min_price_method(self):
        """
        min_price Methode gibt den niedrigsten Preis zurück
        """
        self.assertEqual(self.offer.min_price(), 50)
    
    def test_min_delivery_time_method(self):
        """
        min_delivery_time Methode gibt die kürzeste Lieferzeit zurück
        """
        self.assertEqual(self.offer.min_delivery_time(), 3)
    
    def test_user_details_in_serializer(self):
        """
        user_details Feld im Serializer gibt korrekte Benutzerdaten zurück (in der Liste)
        """
        url = reverse('offers-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)
        
        # user_details ist nur in der List-View verfügbar
        offer_data = response.data['results'][0]
        self.assertIn('user_details', offer_data)
        self.assertEqual(offer_data['user_details']['first_name'], 'Max')
        self.assertEqual(offer_data['user_details']['last_name'], 'Mustermann')
        self.assertEqual(offer_data['user_details']['username'], 'business1')
    
    def test_offer_string_representation(self):
        """
        __str__ Methode des Offer Models gibt den Titel zurück
        """
        self.assertEqual(str(self.offer), "Test Offer")
    
    def test_offer_detail_string_representation(self):
        """
        __str__ Methode des OfferDetail Models gibt korrekte Darstellung zurück
        """
        basic_detail = OfferDetail.objects.get(offer=self.offer, offer_type='basic')
        self.assertEqual(str(basic_detail), "Test Offer - basic")