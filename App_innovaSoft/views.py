from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Transacion, CuentaDetalle, SubCuenta, LibroMayor
from django.contrib import messages
import json
from django.http import JsonResponse
 


# Create your views here.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")

def libroMayor(request):
    CatalogoCuentas = SubCuenta.objects.all()  # Cambia a CuentaDetalle si quieres este nivel de detalle
    return render(request, 'App_innovaSoft/libroMayor.html', {'CatalogoCuentas': CatalogoCuentas})

def CatalogoCuentas(request):
    return render(request,"App_innovaSoft/CatalogoCuentas.html")

def transaccion(request):
    return render(request,"App_innovaSoft/transaccion.html")


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


