from django.shortcuts import render
from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle

# Create your views here.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")

#def CatalogoCuentas(request):
 #   return render(request,"App_innovaSoft/CatalogoCuentas.html")

#Vistas CatalogoCuentas


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
    subcuentas = SubCuenta.objects.all()  # Cambia esto al modelo correcto de las cuentas

    # Filtrado condicional
    if tipo_cuenta_id and tipo_cuenta_id != '':
        subcuentas = subcuentas.filter(idDeMayor__idRubro__idGrupoCuenta=tipo_cuenta_id)

    if rubro_id and rubro_id != '':
        subcuentas = subcuentas.filter(idDeMayor__idRubro__idRubro=rubro_id)

    if cuenta_mayor_id and cuenta_mayor_id != '':
        subcuentas = subcuentas.filter(idDeMayor__idDeMayor=cuenta_mayor_id)

    # Agregar las subcuentas filtradas al contexto
    context = {
        'tipos_cuenta': tipos_cuenta,
        'rubros': rubros,
        'cuentas_mayor': cuentas_mayor,
        'subcuentas': subcuentas,  # Incluye las subcuentas filtradas
    }

    return render(request, 'App_innovaSoft/CatalogoCuentas.html', context)
