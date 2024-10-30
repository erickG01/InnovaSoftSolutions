"""
Configuración de URLs para el proyecto InnovaSoftSolutions.

La lista `urlpatterns` mapea URLs a vistas. Para más información, consulta:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Ejemplos:
Vistas basadas en funciones:
    1. Agrega una importación: from my_app import views
    2. Agrega una URL a urlpatterns: path('', views.home, name='home')
Vistas basadas en clases:
    1. Agrega una importación: from other_app.views import Home
    2. Agrega una URL a urlpatterns: path('', Home.as_view(), name='home')
Incluyendo otra configuración de URL:
    1. Importa la función include(): from django.urls import include, path
    2. Agrega una URL a urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App_innovaSoft import views 

urlpatterns = [
    path('admin/', admin.site.urls),                                                   # Ruta para el panel de administración
    path('inicio/',views.home,name="inicio"),                                          # Ruta para la vista de inicio
    path('LibroMayor/',views.libroMayor,name="libroMayor"),                            # Ruta para la vista de Libro Mayor
    path('CatalogoCuentas/',views.CatalogoCuentas,name="CatalogoCuentas"),             # Ruta para el catálogo de cuentas
    path('HojAjustes/',views.hojAjustes,name="hojAjustes"),                            # Ruta para la hoja de ajustes
]