# config/urls.py - JSON FORMATINDA QAYTAR
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views import View
from drf_spectacular.views import SpectacularAPIView

# ✅ JSON FORMATINDA OPENAPI
class JSONOpenAPI(View):
    def get(self, request):
        # Spectacular view-dən məlumatı al
        spectacular_view = SpectacularAPIView.as_view()
        response = spectacular_view(request)
        
        # JSON formatında qaytar
        return JsonResponse(response.data)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('analitic.urls')),
    path('', lambda request: redirect('admin/', permanent=False)),
    path('openapi.json', JSONOpenAPI.as_view()),  # ✅ JSON formatında
]