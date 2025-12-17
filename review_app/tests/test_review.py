from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from profile_app.models import Profile
from review_app.models import Reviews


# ========================================
# HAPPY PATH TESTS
# ========================================

class GetReviewsHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Abrufen von Bewertungen (GET /api/reviews/)"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user1 = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user1, type='business')
        
        self.business_user2 = User.objects.create_user(username='business2', password='testpass123')
        Profile.objects.create(user=self.business_user2, type='business')
        
        # Customer Users erstellen
        self.customer_user1 = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user1, type='customer')
        
        self.customer_user2 = User.objects.create_user(username='customer2', password='testpass123')
        Profile.objects.create(user=self.customer_user2, type='customer')
        
        # Bewertungen erstellen
        self.review1 = Reviews.objects.create(
            business_user=self.business_user1,
            reviewer=self.customer_user1,
            rating=4,
            description="Sehr professioneller Service."
        )
        
        self.review2 = Reviews.objects.create(
            business_user=self.business_user1,
            reviewer=self.customer_user2,
            rating=5,
            description="Top Qualität und schnelle Lieferung!"
        )
        
        self.review3 = Reviews.objects.create(
            business_user=self.business_user2,
            reviewer=self.customer_user1,
            rating=3,
            description="Ganz okay."
        )
        
        self.client.force_authenticate(user=self.customer_user1)
    
    def test_get_all_reviews(self):
        """
        Authentifizierte Benutzer können alle Bewertungen abrufen (Status 200)
        """
        url = reverse('reviews-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_get_reviews_filter_by_business_user_id(self):
        """
        Bewertungen können nach business_user_id gefiltert werden (Status 200)
        """
        url = reverse('reviews-list')
        response = self.client.get(url, {'business_user_id': self.business_user1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review['business_user'], self.business_user1.id)
    
    def test_get_reviews_filter_by_reviewer_id(self):
        """
        Bewertungen können nach reviewer_id gefiltert werden (Status 200)
        """
        url = reverse('reviews-list')
        response = self.client.get(url, {'reviewer_id': self.customer_user1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for review in response.data:
            self.assertEqual(review['reviewer'], self.customer_user1.id)
    
    def test_get_reviews_ordered_by_updated_at(self):
        """
        Bewertungen können nach updated_at sortiert werden (Status 200)
        """
        url = reverse('reviews-list')
        response = self.client.get(url, {'ordering': 'updated_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
    
    def test_get_reviews_ordered_by_rating(self):
        """
        Bewertungen können nach rating sortiert werden (Status 200)
        """
        url = reverse('reviews-list')
        response = self.client.get(url, {'ordering': 'rating'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        # Niedrigste Bewertung zuerst
        self.assertEqual(response.data[0]['rating'], 3)
    
    def test_get_reviews_as_business_user(self):
        """
        Business User können auch Bewertungen abrufen (Status 200)
        """
        self.client.force_authenticate(user=self.business_user1)
        url = reverse('reviews-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class PostReviewHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Erstellen von Bewertungen (POST /api/reviews/)"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        self.client.force_authenticate(user=self.customer_user)
    
    def test_post_review_as_customer_user(self):
        """
        Customer User können erfolgreich eine Bewertung erstellen (Status 201)
        """
        url = reverse('reviews-list')
        payload = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Alles war toll!'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['reviewer'], self.customer_user.id)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['description'], 'Alles war toll!')
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)


class PatchReviewHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Aktualisieren von Bewertungen (PATCH /api/reviews/{id}/)"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen (Ersteller der Bewertung)
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        # Bewertung erstellen
        self.review = Reviews.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Sehr professioneller Service."
        )
        
        self.client.force_authenticate(user=self.customer_user)
    
    def test_patch_review_rating_only(self):
        """
        Ersteller kann nur das rating aktualisieren (Status 200)
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'rating': 5
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], "Sehr professioneller Service.")
    
    def test_patch_review_description_only(self):
        """
        Ersteller kann nur die description aktualisieren (Status 200)
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'description': 'Noch besser als erwartet!'
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['description'], 'Noch besser als erwartet!')
    
    def test_patch_review_rating_and_description(self):
        """
        Ersteller kann rating und description gleichzeitig aktualisieren (Status 200)
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'rating': 5,
            'description': 'Noch besser als erwartet!'
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['description'], 'Noch besser als erwartet!')
        # updated_at sollte aktualisiert werden
        self.assertIn('updated_at', response.data)


class DeleteReviewHappyPathTests(APITestCase):
    """Tests für das erfolgreiche Löschen von Bewertungen (DELETE /api/reviews/{id}/)"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen (Ersteller der Bewertung)
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
        
        # Bewertung erstellen
        self.review = Reviews.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Test Review"
        )
        
        self.client.force_authenticate(user=self.customer_user)
    
    def test_delete_review_as_creator(self):
        """
        Ersteller der Bewertung kann diese erfolgreich löschen (Status 204)
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Bewertung sollte nicht mehr existieren
        self.assertFalse(Reviews.objects.filter(id=self.review.id).exists())


# ========================================
# UNHAPPY PATH TESTS
# ========================================

class GetReviewsUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene GET-Requests"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
    
    def test_get_reviews_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können keine Bewertungen abrufen (Status 401)
        """
        url = reverse('reviews-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostReviewUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene POST-Requests"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User erstellen
        self.customer_user = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user, type='customer')
    
    def test_post_review_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können keine Bewertung erstellen (Status 401)
        """
        url = reverse('reviews-list')
        payload = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Test'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_post_review_as_business_user(self):
        """
        Business User können keine Bewertungen erstellen (Status 403)
        """
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-list')
        payload = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Test'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_post_review_without_profile(self):
        """
        Benutzer ohne Profil können keine Bewertungen erstellen (Status 403)
        """
        user_without_profile = User.objects.create_user(username='noprofile', password='testpass123')
        self.client.force_authenticate(user=user_without_profile)
        
        url = reverse('reviews-list')
        payload = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': 'Test'
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_post_review_missing_required_fields(self):
        """
        Bewertung ohne erforderliche Felder schlägt fehl (Status 400)
        """
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('reviews-list')
        payload = {
            'rating': 4
            # business_user fehlt
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user', response.data)


class PatchReviewUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene PATCH-Requests"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User 1 (Ersteller der Bewertung)
        self.customer_user1 = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user1, type='customer')
        
        # Customer User 2 (nicht der Ersteller)
        self.customer_user2 = User.objects.create_user(username='customer2', password='testpass123')
        Profile.objects.create(user=self.customer_user2, type='customer')
        
        # Bewertung erstellen
        self.review = Reviews.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user1,
            rating=4,
            description="Test Review"
        )
    
    def test_patch_review_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können keine Bewertung aktualisieren (Status 401)
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'rating': 5
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_patch_review_by_non_creator(self):
        """
        Andere Benutzer können die Bewertung nicht bearbeiten (Status 403)
        """
        self.client.force_authenticate(user=self.customer_user2)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'rating': 5
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_patch_review_by_business_user(self):
        """
        Business User können die Bewertung nicht bearbeiten (Status 403)
        """
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'rating': 5
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_patch_review_non_existent(self):
        """
        Bewertung mit nicht existierender ID kann nicht aktualisiert werden (Status 404)
        """
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': 99999})
        payload = {
            'rating': 5
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_patch_review_with_disallowed_fields(self):
        """
        Versuch, nicht editierbare Felder zu ändern, schlägt fehl (Status 400)
        """
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        payload = {
            'business_user': self.business_user.id,  # Nicht erlaubt
            'rating': 5
        }
        response = self.client.patch(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user', response.data)


class DeleteReviewUnhappyPathTests(APITestCase):
    """Tests für fehlgeschlagene DELETE-Requests"""
    
    def setUp(self):
        # Business User erstellen
        self.business_user = User.objects.create_user(username='business1', password='testpass123')
        Profile.objects.create(user=self.business_user, type='business')
        
        # Customer User 1 (Ersteller der Bewertung)
        self.customer_user1 = User.objects.create_user(username='customer1', password='testpass123')
        Profile.objects.create(user=self.customer_user1, type='customer')
        
        # Customer User 2 (nicht der Ersteller)
        self.customer_user2 = User.objects.create_user(username='customer2', password='testpass123')
        Profile.objects.create(user=self.customer_user2, type='customer')
        
        # Bewertung erstellen
        self.review = Reviews.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user1,
            rating=4,
            description="Test Review"
        )
    
    def test_delete_review_unauthenticated(self):
        """
        Nicht authentifizierte Benutzer können keine Bewertung löschen (Status 401)
        """
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_delete_review_by_non_creator(self):
        """
        Andere Benutzer können die Bewertung nicht löschen (Status 403)
        """
        self.client.force_authenticate(user=self.customer_user2)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_review_by_business_user(self):
        """
        Business User können die Bewertung nicht löschen (Status 403)
        """
        self.client.force_authenticate(user=self.business_user)
        url = reverse('reviews-detail', kwargs={'pk': self.review.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_review_non_existent(self):
        """
        Bewertung mit nicht existierender ID kann nicht gelöscht werden (Status 404)
        """
        self.client.force_authenticate(user=self.customer_user1)
        url = reverse('reviews-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
