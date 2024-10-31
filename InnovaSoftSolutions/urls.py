"""
URL configuration for InnovaSoftSolutions project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App_innovaSoft import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/',views.home,name="inicio"),
    path('LibroMayor/',views.libroMayor,name="libroMayor"),
    path('CatalogoCuentas/',views.CatalogoCuentas,name="CatalogoCuentas"),
    path('login/', views.login,name="login"),
    path('transaccion/',views.transaccion,name="transaccion"),
    path('agregar/',views.agregar_transaccion, name='agregar_transaccion'),
    path('logout/', views.logout,name="logout"),
    path('guardar_transacciones/', views.guardar_transacciones, name='guardar_transacciones'),
    
]

 




