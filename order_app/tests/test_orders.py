from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from profile_app.models import Profile
from offer_app.models import Offer, OfferDetail
from order_app.models import Orders


class OrdersAPIHappyPathTestCase(APITestCase):
    """Tests für erfolgreiche Order-Operationen (Happy Paths)"""

    def setUp(self):
        # Customer User erstellen
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='testpass123'
        )
        Profile.objects.create(
            user=self.customer_user,
            type='customer',
            first_name='Max',
            last_name='Mustermann'
        )

        # Business User erstellen
        self.business_user = User.objects.create_user(
            username='business1',
            password='testpass123'
        )
        Profile.objects.create(
            user=self.business_user,
            type='business',
            first_name='Anna',
            last_name='Business'
        )

        # Admin User erstellen
        self.admin_user = User.objects.create_user(
            username='admin1',
            password='testpass123',
            is_staff=True
        )

        # Offer und OfferDetail erstellen
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Logo Design',
            description='Professional logo design'
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Logo Design Basic',
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=['Logo', 'Visitenkarten'],
            offer_type='basic'
        )

        # Order erstellen für Tests
        self.order = Orders.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer_user,
            business_user=self.business_user,
            status='in_progress'
        )

    def test_order_list_as_authenticated_user_success(self):
        """GET /api/orders/ - Authenticated User kann seine Orders sehen"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('orders-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_order_list_shows_customer_orders(self):
        """GET /api/orders/ - Customer sieht nur seine eigenen Orders"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('orders-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Prüfe, dass nur Orders angezeigt werden, bei denen der User beteiligt ist
        for order in response.data:
            self.assertTrue(
                order['customer_user'] == self.customer_user.id or 
                order['business_user'] == self.customer_user.id
            )

    def test_order_list_shows_business_orders(self):
        """GET /api/orders/ - Business User sieht seine Business Orders"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_order_as_customer_success(self):
        """POST /api/orders/ - Customer kann Order erstellen"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('orders-list')
        
        data = {
            'offer_detail_id': self.offer_detail.id,
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer_user.id)
        self.assertEqual(response.data['business_user'], self.business_user.id)
        self.assertEqual(response.data['status'], 'in_progress')

    def test_update_order_status_as_business_user_success(self):
        """PATCH /api/orders/{id}/ - Business User kann Order-Status aktualisieren"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        data = {
            'status': 'completed'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_update_order_status_to_cancelled(self):
        """PATCH /api/orders/{id}/ - Status kann auf cancelled gesetzt werden"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        data = {
            'status': 'cancelled'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_delete_order_as_admin_success(self):
        """DELETE /api/orders/{id}/ - Admin kann Order löschen"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Orders.objects.filter(id=self.order.id).exists())

    def test_get_order_count_for_business_user_success(self):
        """GET /api/order-count/{business_user_id}/ - Order Count abrufen"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-count-in-progress', kwargs={'pk': self.business_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('order_count', response.data)
        self.assertGreaterEqual(response.data['order_count'], 1)

    def test_get_completed_order_count_for_business_user_success(self):
        """GET /api/completed-order-count/{business_user_id}/ - Completed Order Count abrufen"""
        # Order auf completed setzen
        self.order.status = 'completed'
        self.order.save()
        
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-count-completed', kwargs={'pk': self.business_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completed_order_count', response.data)
        self.assertGreaterEqual(response.data['completed_order_count'], 1)


class OrdersAPIUnhappyPathTestCase(APITestCase):
    """Tests für fehlerhafte Order-Operationen (Unhappy Paths)"""

    def setUp(self):
        # Customer User erstellen
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='testpass123'
        )
        Profile.objects.create(
            user=self.customer_user,
            type='customer'
        )

        # Business User erstellen
        self.business_user = User.objects.create_user(
            username='business1',
            password='testpass123'
        )
        Profile.objects.create(
            user=self.business_user,
            type='business'
        )

        # Weiterer Customer User für Permission Tests
        self.other_customer = User.objects.create_user(
            username='customer2',
            password='testpass123'
        )
        Profile.objects.create(
            user=self.other_customer,
            type='customer'
        )

        # Non-admin User
        self.regular_user = User.objects.create_user(
            username='regular1',
            password='testpass123',
            is_staff=False
        )

        # Offer und OfferDetail erstellen
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Logo Design',
            description='Professional logo design'
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Logo Design Basic',
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=['Logo'],
            offer_type='basic'
        )

        # Order erstellen
        self.order = Orders.objects.create(
            offer_detail=self.offer_detail,
            customer_user=self.customer_user,
            business_user=self.business_user,
            status='in_progress'
        )

    def test_order_list_without_authentication_fails(self):
        """GET /api/orders/ - Unauthenticated User wird abgelehnt (401)"""
        url = reverse('orders-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_without_authentication_fails(self):
        """POST /api/orders/ - Unauthenticated User kann keine Order erstellen (401)"""
        url = reverse('orders-list')
        
        data = {
            'offer_detail_id': self.offer_detail.id,
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_as_business_user_fails(self):
        """POST /api/orders/ - Business User kann keine Order erstellen (403)"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-list')
        
        data = {
            'offer_detail_id': self.offer_detail.id,
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_with_invalid_offer_detail_fails(self):
        """POST /api/orders/ - Order mit ungültiger offer_detail_id (400)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('orders-list')
        
        data = {
            'offer_detail_id': 99999,  # Existiert nicht
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_as_customer_fails(self):
        """PATCH /api/orders/{id}/ - Customer kann Order-Status nicht ändern (403)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        data = {
            'status': 'completed'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_without_authentication_fails(self):
        """PATCH /api/orders/{id}/ - Unauthenticated User kann Status nicht ändern (401)"""
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        data = {
            'status': 'completed'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order_with_invalid_status_fails(self):
        """PATCH /api/orders/{id}/ - Ungültiger Status wird abgelehnt (400)"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        data = {
            'status': 'invalid_status'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_non_existent_order_fails(self):
        """PATCH /api/orders/{id}/ - Update nicht existierender Order (404)"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-detail', kwargs={'pk': 99999})
        
        data = {
            'status': 'completed'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_as_customer_fails(self):
        """DELETE /api/orders/{id}/ - Customer kann Order nicht löschen (403)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_as_business_user_fails(self):
        """DELETE /api/orders/{id}/ - Business User kann Order nicht löschen (403)"""
        self.client.force_authenticate(user=self.business_user)
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_without_authentication_fails(self):
        """DELETE /api/orders/{id}/ - Unauthenticated User kann nicht löschen (401)"""
        url = reverse('orders-detail', kwargs={'pk': self.order.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_non_existent_order_fails(self):
        """DELETE /api/orders/{id}/ - Löschen nicht existierender Order (404)"""
        self.client.force_authenticate(user=self.regular_user)
        self.regular_user.is_staff = True
        self.regular_user.save()
        
        url = reverse('orders-detail', kwargs={'pk': 99999})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_count_without_authentication_fails(self):
        """GET /api/order-count/{business_user_id}/ - Unauthenticated (401)"""
        url = reverse('order-count-in-progress', kwargs={'pk': self.business_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_count_for_non_business_user_fails(self):
        """GET /api/order-count/{business_user_id}/ - Customer User statt Business User (404)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-count-in-progress', kwargs={'pk': self.customer_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User is not a business user', str(response.data))

    def test_get_order_count_for_non_existent_user_fails(self):
        """GET /api/order-count/{business_user_id}/ - Nicht existierender User (404)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-count-in-progress', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_completed_order_count_without_authentication_fails(self):
        """GET /api/completed-order-count/{business_user_id}/ - Unauthenticated (401)"""
        url = reverse('order-count-completed', kwargs={'pk': self.business_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_completed_order_count_for_non_business_user_fails(self):
        """GET /api/completed-order-count/{business_user_id}/ - Customer User (404)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-count-completed', kwargs={'pk': self.customer_user.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User is not a business user', str(response.data))

    def test_get_completed_order_count_for_non_existent_user_fails(self):
        """GET /api/completed-order-count/{business_user_id}/ - Nicht existierender User (404)"""
        self.client.force_authenticate(user=self.customer_user)
        url = reverse('order-count-completed', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)