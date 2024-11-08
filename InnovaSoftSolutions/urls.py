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
from App_innovaSoft.views import get_rubros, get_cuentas_mayor

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login,name="login"),
    path('logout/', views.logout,name="logout"),
    path('', views.home, name='home'),  # Ruta para la raíz
    path('inicio/',views.home,name="inicio"),

    path('CatalogoCuentas/', views.tipos_cuentas, name="CatalogoCuentas"),
    path('nuevaCuenta/', views.nuevaCuenta, name="nuevaCuenta"),
    path('Costos/',views.Costos,name="costos"),
    path('costos/', views.calcular_costos_indirectos, name='costos'),
    path('LibroMayor/',views.libro_mayor_view,name="libroMayor"),
    path('transacciones/', views.transaccion_view, name='transaccion'),  # Transacciones
    #path('agregar/',views.agregar_transaccion, name='agregar_transaccion'),
    path('BalanceDeComprobacion',views.generar_balance_de_comprobacion,name="BalanceDeComprobacion"),
    path('EstadoDeResultados',views.generar_estado_de_resultados,name='EstadoDeResultados'),
    path('estadoCapital/',views.estadoCapital,name="estadoCapital"),
    path('EstadoFinancieros/', views.estadoFinancieros, name="estadoFinancieros"), # Ruta para estados financieros
    path('balanceGeneral/',views.balanceGeneral,name="balanceGeneral"),
    path('save_transactions/', views.save_transactions, name='save_transactions'),
    path('obtener_transacciones/', views.obtener_transacciones, name='obtener_transacciones'),
    path('calcular-totales/', views.calcular_totales, name='calcular_totales'),
    path('inventario/',views.mostrar_activos,name='inventario'),
    path('get_rubros/<int:tipo_id>/', get_rubros, name='get_rubros'),
    path('get_cuentas_mayor/<int:rubro_id>/', get_cuentas_mayor, name='get_cuentas_mayor'),
    path('api/departamentos/', views.obtener_departamentos, name='obtener_departamentos'),
    path('api/empleados/<int:departamento_id>/', views.obtener_empleados, name='obtener_empleados'),
    path('guardar_orden/', views.guardar_orden_trabajo, name='guardar_orden'),
    path('get-orden-data/<int:orden_id>/', views.get_orden_data, name='get_orden_data'),
]