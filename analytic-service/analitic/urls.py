# analitic/urls.py - DÜZƏLDİN
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewViewSet, ProductViewViewSet, AnalyticsProductViewSet, OrderAnalyticsViewSet

router = DefaultRouter()
router.register(r'shop-views', ShopViewViewSet, basename='shop-view')
router.register(r'product-views', ProductViewViewSet, basename='product-view')
router.register(r'analytics-products', AnalyticsProductViewSet, basename='analytics-product')
router.register(r'order-analytics', OrderAnalyticsViewSet, basename='order-analytics')

urlpatterns = [
    path('', include(router.urls)),
    path('receive-order/', OrderAnalyticsViewSet.as_view({'post': 'receive_order'}), name='receive-order'),
]

# ✅ DRF Spectacular üçün AYRICA URL ƏLAVƏ EDİN
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]