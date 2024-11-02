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
    path('admin/', admin.site.urls),
    path('login/', views.login,name="login"),
    path('logout/', views.logout,name="logout"),
    path('', views.home, name='home'),  # Ruta para la raíz
    path('inicio/',views.home,name="inicio"),

    path('CatalogoCuentas/', views.tipos_cuentas, name="CatalogoCuentas"),
    path('Costos/',views.Costos,name="costos"),
    path('LibroMayor/',views.libro_mayor_view,name="libroMayor"),
    path('BalanceDeComprobacion',views.generar_balance_de_comprobacion,name="BalanceDeComprobacion"),
    path('EstadoDeResultados',views.generar_estado_de_resultados,name='EstadoDeResultados'),
    path('estadoCapital/',views.estadoCapital,name="estadoCapital"),
    path('HojAjustes/',views.hojAjustes,name="hojAjustes"),
    path('transacciones/', views.transaccion, name='transaccion'),  # Transacciones
    path('EstadoFinancieros/', views.estadoFinancieros, name="estadoFinancieros"), # Ruta para estados financieros
    #path('agregar/',views.agregar_transaccion, name='agregar_transaccion'),

    path('transaccion/',views.transaccion,name="transaccion"),   
]