# analitic/urls.py - DÜZƏLDİLMİŞ
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewViewSet, ProductViewViewSet, AnalyticsViewSet

router = DefaultRouter()
router.register(r'shop-view', ShopViewViewSet, basename='shop-view')
router.register(r'product-view', ProductViewViewSet, basename='product-view')
router.register(r'', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),  
]