from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from ..models import Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user_id=str(self.user.id))
        self.order_item = OrderItem.objects.create(order=self.order, quantity=2, status=1)

    def test_get_orders_list(self):
        url = reverse('orders-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_create_order(self):
        url = reverse('orders-list-create')
        data = {"user_id": str(self.user.id)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_order_detail(self):
        url = reverse('orders-detail', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_patch_order_detail(self):
        url = reverse('orders-detail', args=[self.order.id])
        data = {"status": 2}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 2)

    def test_delete_order(self):
        url = reverse('orders-detail', args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())


class OrderItemTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user_id=str(self.user.id))
        self.order_item = OrderItem.objects.create(order=self.order, quantity=2, status=1)

    def test_get_orderitems_list(self):
        url = reverse('orderitems-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_orderitem(self):
        url = reverse('orderitems-list-create')
        data = {"order": self.order.id, "quantity": 3, "status": 1}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_orderitem_detail(self):
        url = reverse('orderitems-detail', args=[self.order_item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_orderitem_detail(self):
        url = reverse('orderitems-detail', args=[self.order_item.id])
        data = {"quantity": 5}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order_item.refresh_from_db()
        self.assertEqual(self.order_item.quantity, 5)

    def test_delete_orderitem(self):
        url = reverse('orderitems-detail', args=[self.order_item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(OrderItem.objects.filter(id=self.order_item.id).exists())


class ShopcartOrderTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('order_service.views.views_v1.shopcart_client.get_shopcart_data')
    @patch('order_service.views.views_v1.product_client.get_variation')
    @patch('order_service.views.views_v1.product_client.get_product')
    @patch('order_service.views.views_v1.publisher.publish_order_created')
    def test_create_order_from_shopcart(self, mock_publish, mock_get_product, mock_get_variation, mock_get_shopcart):
        mock_get_shopcart.return_value = {
            "id": "cart123",
            "items": [{"product_variation_id": "var1", "product_variation": 1, "quantity": 2}]
        }
        mock_get_variation.return_value = {"product_id": "prod1"}
        mock_get_product.return_value = {"shop_id": "shop1"}
        mock_publish.return_value = True

        url = reverse('create-order-from-shopcart')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_id", response.data)
        self.assertEqual(response.data["items_count"], 1)




# import pytest
# from rest_framework import status
# from rest_framework.test import APIClient
# from django.urls import reverse
# from order_service.orders.models import Order, OrderItem


# @pytest.fixture
# def api_client():
#     return APIClient()


# @pytest.fixture
# def sample_order(db):
#     return Order.objects.create(user_id=10)


# @pytest.fixture
# def sample_item(db, sample_order):
#     return OrderItem.objects.create(
#         order=sample_order,
#         product_variation=1,
#         quantity=2,
#         price=10,
#         status=1
#     )


# # 1️⃣ GET + POST /orders/
# @pytest.mark.django_db
# def test_orders_list_get(api_client, sample_order):
#     url = reverse("orders_list_create")
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) >= 1


# @pytest.mark.django_db
# def test_orders_create(api_client):
#     url = reverse("orders_list_create")
#     data = {"user_id": 11}
#     response = api_client.post(url, data, format="json")
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data["user_id"] == 11


# # 2️⃣ GET / PATCH / DELETE /orders/<id>/
# @pytest.mark.django_db
# def test_order_detail_get(api_client, sample_order):
#     url = reverse("orders_detail", args=[sample_order.id])
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["id"] == sample_order.id


# @pytest.mark.django_db
# def test_order_detail_patch(api_client, sample_order):
#     url = reverse("orders_detail", args=[sample_order.id])
#     data = {"user_id": 22}
#     response = api_client.patch(url, data, format="json")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["user_id"] == 22


# @pytest.mark.django_db
# def test_order_detail_delete(api_client, sample_order):
#     url = reverse("orders_detail", args=[sample_order.id])
#     response = api_client.delete(url)
#     assert response.status_code == status.HTTP_204_NO_CONTENT


# # 3️⃣ GET + POST /order-items/
# @pytest.mark.django_db
# def test_orderitems_list_get(api_client, sample_item):
#     url = reverse("orderitems_list_create")
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     assert len(response.data) >= 1


# @pytest.mark.django_db
# def test_orderitems_create(api_client, sample_order):
#     url = reverse("orderitems_list_create")
#     data = {
#         "order": sample_order.id,
#         "product_variation": 5,
#         "quantity": 3,
#         "price": 25
#     }
#     response = api_client.post(url, data, format="json")
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data["order"] == sample_order.id


# # 4️⃣ GET / PATCH / DELETE /order-items/<id>/
# @pytest.mark.django_db
# def test_orderitems_detail_get(api_client, sample_item):
#     url = reverse("orderitems_detail", args=[sample_item.id])
#     response = api_client.get(url)
#     assert response.status_code == status.HTTP_200_OK


# @pytest.mark.django_db
# def test_orderitems_detail_patch(api_client, sample_item):
#     url = reverse("orderitems_detail", args=[sample_item.id])
#     data = {"quantity": 10}
#     response = api_client.patch(url, data, format="json")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["quantity"] == 10


# @pytest.mark.django_db
# def test_orderitems_detail_delete(api_client, sample_item):
#     url = reverse("orderitems_detail", args=[sample_item.id])
#     response = api_client.delete(url)
#     assert response.status_code == status.HTTP_204_NO_CONTENT


# # 5️⃣ POST /create-order-from-shopcart/
# @pytest.mark.django_db
# def test_create_order_from_shopcart(api_client):
#     url = reverse("create_order_from_shopcart")
#     data = {
#         "user_id": 33,
#         "items": [
#             {"product_variation": 1, "quantity": 2, "price": 50},
#             {"product_variation": 2, "quantity": 1, "price": 20},
#         ],
#     }
#     response = api_client.post(url, data, format="json")
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data["message"] == "Order created successfully"


# # 6️⃣ PATCH /update-order-item-status/<id>/
# @pytest.mark.django_db
# def test_update_order_item_status(api_client, sample_item, monkeypatch):
#     # mock send_order_completed_event
#     monkeypatch.setattr("order_service.tasks.send_order_completed_event", lambda x: None)
    
#     url = reverse("update_order_item_status", args=[sample_item.id])
#     data = {"status": 3}
#     response = api_client.patch(url, data, format="json")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data["status"] == 3


