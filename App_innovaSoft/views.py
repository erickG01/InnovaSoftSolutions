from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Transacion, CuentaDetalle, SubCuenta, LibroMayor
from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render
from django.db.models import Sum, F
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from django.http import HttpResponse
from decimal import Decimal
from reportlab.lib.units import inch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json





# Create your views here.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")

def PeriodoContable(request):
    return render(request,"App_innovaSoft/PeriodoContable.html")

def libroMayor(request):
    CatalogoCuentas = SubCuenta.objects.all()  # Cambia a CuentaDetalle si quieres este nivel de detalle
    return render(request, 'App_innovaSoft/libroMayor.html', {'CatalogoCuentas': CatalogoCuentas})

def CatalogoCuentas(request):
    return render(request,"App_innovaSoft/CatalogoCuentas.html")


#def CatalogoCuentas(request):
 #   return render(request,"App_innovaSoft/CatalogoCuentas.html")

# Vistas CatalogoCuentas
def transaccion(request):
    CatalogoCuentas = SubCuenta.objects.all()  # Cambia a CuentaDetalle si quieres este nivel de detalle
    return render(request, 'App_innovaSoft/transaccion.html', {'CatalogoCuentas': CatalogoCuentas})

# Vistas CatalogoCuentas
def obtener_catalogo_cuentas(request):
    CatalogoCuentas = SubCuenta.objects.all()
    cuentas_json = [{"id": cuenta.idSubCuenta, "nombre": cuenta.nombre} for cuenta in CatalogoCuentas]
    return JsonResponse(cuentas_json, safe=False)


#Guardar transaccion
@require_POST
def guardar_transaccion(request):
    if request.method == 'POST':
        try:
            datos_transacciones = json.loads(request.body)  # Carga los datos JSON enviados
            for transaccion_data in datos_transacciones:
                id_subcuenta = transaccion_data.get('idSubCuenta')
                id_cuenta_detalle = transaccion_data.get('idCuentaDetalle')
                debe = transaccion_data.get('debe', 0)
                haber = transaccion_data.get('haber', 0)

                # Verifica que el idSubCuenta tenga valor
                if not id_subcuenta:
                    return JsonResponse({'status': 'error', 'message': 'Falta el id de SubCuenta en una de las filas'}, status=400)
                
                # Obtener instancias de SubCuenta y CuentaDetalle
                subcuenta = SubCuenta.objects.get(idSubCuenta=id_subcuenta)
                cuenta_detalle = CuentaDetalle.objects.get(id=id_cuenta_detalle)

                # Crear instancia de Transacion
                Transacion.objects.create(
                    idSubCuenta=subcuenta,
                    idCuentaDetalle=cuenta_detalle,
                    debe=debe,
                    haber=haber
                )
                
            return JsonResponse({'status': 'success'}, status=201)
        
        except Exception as e:
            print("Error al guardar transacción:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
pass








from django.contrib.auth import authenticate, login as auth_login

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                if user.is_superuser:
                    return redirect('inicio')  # Redirige a la página de inicio
                else:
                    return redirect('login')
            else:
                messages.error(request, "La cuenta está desactivada.")
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    return render(request, 'App_innovaSoft/login.html')

def logout(request):
    return render (request,"App_innovaSoft/login.html")

def agregar_transaccion(request):
    if request.method == 'POST':
        cuenta_id = request.POST.get('cuenta')
        fecha = request.POST.get('fecha')
        debe = request.POST.get('debe')
        haber = request.POST.get('haber')
        
        # Crea una nueva transacción
        nueva_transaccion = transaccion(
            cuenta_id=cuenta_id,
            fecha=fecha,
            debe=debe,
            haber=haber
        )
        nueva_transaccion.save()
        
        # Redirigir a la página de transacciones después de agregar
        return redirect('transaccion') 

    return render(request, 'App_innovaSoft/transacciones.html', {'catalogo_cuentas': CatalogoCuentas})



def guardar_transacciones(request):
    if request.method == 'POST':
        transacciones_data = json.loads(request.POST.get('transacciones', '[]'))
        
        # Procesar cada transacción y guardarla en el libro mayor
        for transaccion in transacciones_data:
            numero_cuenta = transaccion.get('numeroCuenta')
            nombre_cuenta = transaccion.get('nombreCuenta')
            debe = float(transaccion.get('debe', 0))
            haber = float(transaccion.get('haber', 0))

            # Crear la entrada en el Libro Mayor
            nueva_entrada = LibroMayor(
                numero_cuenta=numero_cuenta,
                nombre_cuenta=nombre_cuenta,
                debe=debe,
                haber=haber,
                # otros campos necesarios
            )
            nueva_entrada.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'fail'}, status=400)


