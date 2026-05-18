from django.contrib import admin
from django.urls import path, include
from django.conf import settings          # ← Añadido para leer tu settings.py
from django.conf.urls.static import static  # ← Añadido para habilitar archivos estáticos

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Tu ruta personalizada de administración
    path('', include('tienda.urls')),
]

# Esto le da permiso a Django de mostrar las imágenes que subas en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)