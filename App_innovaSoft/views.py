
from django.shortcuts import render,redirect
from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle,Transacion
from django.shortcuts import render,  redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login as auth_login
# Create your views here.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")


def Costos(request):
    return render(request,"App_innovaSoft/costos.html")


#def CatalogoCuentas(request):
 #   return render(request,"App_innovaSoft/CatalogoCuentas.html")

#Vistas CatalogoCuentas
def transaccion(request):
    return render(request,"App_innovaSoft/transaccion.html")



def tipos_cuentas(request):
    # Obtener los filtros del request
    tipo_cuenta_id = request.GET.get('tipoCuenta')
    rubro_id = request.GET.get('rubro')
    cuenta_mayor_id = request.GET.get('cuentaMayor')

    # Obtener todos los tipos de cuentas, rubros y cuentas mayores
    tipos_cuenta = GrupoCuenta.objects.all()
    rubros = RubroDeAgrupacion.objects.all()
    cuentas_mayor = CuentaDeMayor.objects.all()

    # Filtrar las subcuentas según los filtros seleccionados
    subcuentas = SubCuenta.objects.select_related('idDeMayor__idRubro__idGrupoCuenta').prefetch_related('detalles')

    # Aplicar filtros si están presentes
    if tipo_cuenta_id:
        subcuentas = subcuentas.filter(idDeMayor__idRubro__idGrupoCuenta=tipo_cuenta_id)

    if rubro_id:
        subcuentas = subcuentas.filter(idDeMayor__idRubro__idRubro=rubro_id)

    if cuenta_mayor_id:
        subcuentas = subcuentas.filter(idDeMayor__idDeMayor=cuenta_mayor_id)

    # Paginación
    paginator = Paginator(subcuentas, 10)  # Mostrar 10 subcuentas por página
    page_number = request.GET.get('page')  # Número de página actual
    page_obj = paginator.get_page(page_number)  # Obtener la página

    # Agregar las subcuentas paginadas al contexto
    context = {
        'tipos_cuenta': tipos_cuenta,
        'rubros': rubros,
        'cuentas_mayor': cuentas_mayor,
        'page_obj': page_obj,  # Usar page_obj en la plantilla
    }

    return render(request, 'App_innovaSoft/CatalogoCuentas.html', context)

def hojAjustes(request):
    return render(request,"App_innovaSoft/hojAjustes.html")

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