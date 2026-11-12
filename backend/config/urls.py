from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.urls import include, path

def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health),
    path('api/v1/auth/', include('accounts.urls')),
]