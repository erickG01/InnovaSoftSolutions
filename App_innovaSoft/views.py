
from django.shortcuts import render,redirect
from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle,Transacion,Informacion,PeriodoContable,Transacion
from django.shortcuts import render,  redirect
from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle,Transacion,Informacion,PeriodoContable
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Sum, F,Q
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from reportlab.lib.units import inch
from django.db.models import Sum, F, Func, Value
from django.db.models.functions import Abs
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import render_to_string
from itertools import zip_longest
from django.db.models.functions import Abs
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from django.urls import reverse
from django.db.models import Max
from itertools import zip_longest
from decimal import Decimal, ROUND_HALF_UP

# Create your views here.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")


def Costos(request):
    return render(request,"App_innovaSoft/costos.html")

def estadoFinancieros(request):
    return render(request, 'App_innovaSoft/estadoFinancieros.html')     # Renderiza la plantilla de estados financieros

#def CatalogoCuentas(request):
 #   return render(request,"App_innovaSoft/CatalogoCuentas.html")

#Vistas CatalogoCuentas
def transaccion(request):
    return render(request,"App_innovaSoft/transaccion.html")


#METODO PARA CONSULTAR LAS CUENTAS
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



# Vista para agregar nueva cuenta al catálogo
def nuevaCuenta(request):
    # Obtener todos los tipos de cuentas, rubros y cuentas mayores
    tipos_cuenta = GrupoCuenta.objects.all()
    rubros = RubroDeAgrupacion.objects.all()
    cuentas_mayor = CuentaDeMayor.objects.all()

    if request.method == 'POST':
        subcuenta_nombre = request.POST.get('subcuenta')
        cuenta_mayor_id = request.POST.get('cuentaMayor')
        cuenta_detalle_nombre = request.POST.get('cuentaDetalle')  # Recibir el nombre de la cuenta detalle
        cuenta_detalle_nombre2 = request.POST.get('cuentaDetalle2')  # Recibir el nombre de la cuenta detalle2
        subcuenta_existente_id = request.POST.get('subcuentaExistente')  # Obtener la subcuenta seleccionada

        # Validación: asegurarse de que se proporcionen los datos necesarios
        if subcuenta_nombre and cuenta_mayor_id:
            try:
                # Obtener el idDeMayor como entero
                id_mayor = int(cuenta_mayor_id)
                # Obtener el objeto CuentaDeMayor
                cuenta_mayor = CuentaDeMayor.objects.get(idDeMayor=id_mayor)
                prefijo = cuenta_mayor.codigoCuenta[:4]  # Obtener los primeros cuatro dígitos del codigoCuenta
                
                # ------------------- SECCIÓN DE SUBCUENTAS -------------------
                # Obtener el último idSubCuenta registrado en la tabla
                ultimo_id_subcuenta = SubCuenta.objects.aggregate(Max('idSubCuenta'))['idSubCuenta__max']
                nuevo_id_subcuenta = (ultimo_id_subcuenta + 1) if ultimo_id_subcuenta is not None else 1  # Empezar desde 1 si no hay registros
                
                # Generar el siguiente sufijo numérico basado en las subcuentas existentes
                subcuentas = SubCuenta.objects.filter(idDeMayor_id=id_mayor)
                ultimo_codigo_subcuenta = subcuentas.aggregate(Max('codigoCuenta'))['codigoCuenta__max']
                nuevo_sufijo_subcuenta = "01"  # Valor por defecto
                
                if ultimo_codigo_subcuenta:
                    ultimo_sufijo_subcuenta = int(ultimo_codigo_subcuenta.split('.')[1])
                    nuevo_sufijo_subcuenta = f"{ultimo_sufijo_subcuenta + 1:02d}" if ultimo_sufijo_subcuenta < 99 else None
                
                # Validación de límite en el sufijo
                if not nuevo_sufijo_subcuenta:
                    messages.error(request, 'No se puede crear más subcuentas para esta cuenta de mayor.')
                    return redirect('nuevaCuenta')

                # Crear y guardar la nueva subcuenta
                codigo_cuenta = f"{prefijo}.{nuevo_sufijo_subcuenta}"
                subcuenta = SubCuenta(
                    idSubCuenta=nuevo_id_subcuenta,  # Usar el ID generado manualmente
                    idDeMayor_id=cuenta_mayor_id,
                    codigoCuenta=codigo_cuenta,
                    nombre=subcuenta_nombre
                )
                subcuenta.save()
                # ------------------------------------------------------------

                # ------------------- SECCIÓN DE CUENTAS DETALLE -------------------
                # Verificar si se debe crear una Cuenta Detalle desde el input 1 o desde la subcuenta existente
                if cuenta_detalle_nombre:
                    # Crear la cuenta detalle con el nombre ingresado
                    cuenta_detalle = crearCuentaDetalle(subcuenta, cuenta_detalle_nombre)
                    messages.success(request, f'Subcuenta "{subcuenta_nombre}" y Cuenta Detalle "{cuenta_detalle_nombre}" creadas con éxito.')
                else:
                    messages.error(request, 'Debe proporcionar el nombre de la Cuenta Detalle o seleccionar una Subcuenta existente para crearla.')

            except CuentaDeMayor.DoesNotExist:
                messages.error(request, 'La Cuenta Mayor seleccionada no existe.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado: {e}')

        # Si se intenta crear solo una cuenta detalle, se puede omitir la validación de subcuenta y cuenta mayor
        elif cuenta_detalle_nombre2 and subcuenta_existente_id:
            # Aquí va la lógica para crear la cuenta detalle desde la subcuenta existente
            try:
                subcuenta_existente = SubCuenta.objects.get(idSubCuenta=subcuenta_existente_id)
                cuenta_detalle = crearCuentaDetalle(subcuenta_existente, cuenta_detalle_nombre2)
                messages.success(request, f'Cuenta Detalle "{cuenta_detalle_nombre2}" creada con éxito desde la Subcuenta seleccionada.')
            except SubCuenta.DoesNotExist:
                messages.error(request, 'La Subcuenta seleccionada no existe.')

        else:
            messages.error(request, 'Debe ingresar el nombre de la Subcuenta y seleccionar la Cuenta Mayor, o proporcionar el nombre de la Cuenta Detalle y seleccionar una Subcuenta existente.')

        return redirect('CatalogoCuentas')

    return render(request, 'App_innovaSoft/nuevaCuenta.html', {
        'tipos_cuenta': tipos_cuenta,
        'rubros': rubros,
        'cuentas_mayor': cuentas_mayor,
         'subcuentas': SubCuenta.objects.all(),  # Asegúrate de que esto siempre esté actualizado
    })

def crearCuentaDetalle(subcuenta, nombre):
    # Obtener el último idCuentaDetalle registrado
    ultimo_id_cuenta_detalle = CuentaDetalle.objects.aggregate(Max('idCuentaDetalle'))['idCuentaDetalle__max']
    nuevo_id_cuenta_detalle = (ultimo_id_cuenta_detalle + 1) if ultimo_id_cuenta_detalle is not None else 1  # Empezar desde 1 si no hay registros

    # Obtener el último código de CuentaDetalle para generar el nuevo código
    ultimo_codigo_cuenta_detalle = CuentaDetalle.objects.filter(idCuenta=subcuenta).aggregate(Max('codigoCuenta'))['codigoCuenta__max']

    # Generar el siguiente sufijo numérico basado en el último código de CuentaDetalle
    nuevo_sufijo_detalle = "01"  # Valor por defecto
    if ultimo_codigo_cuenta_detalle:
        ultimo_sufijo_detalle = int(ultimo_codigo_cuenta_detalle.split('.')[-1])
        nuevo_sufijo_detalle = f"{ultimo_sufijo_detalle + 1:02d}" if ultimo_sufijo_detalle < 99 else None

    # Validación de límite en el sufijo
    if not nuevo_sufijo_detalle:
        raise Exception('No se puede crear más cuentas detalle para esta subcuenta.')

    # Crear el código para la Cuenta Detalle basado en el código de la SubCuenta
    nuevo_codigo_cuenta_detalle = f"{subcuenta.codigoCuenta}.{nuevo_sufijo_detalle}"

    # Crear y guardar la nueva cuenta detalle
    cuenta_detalle = CuentaDetalle(
        idCuenta=subcuenta,  # Relacionar con la subcuenta
        idCuentaDetalle=nuevo_id_cuenta_detalle,  # Usar el ID generado manualmente
        codigoCuenta=nuevo_codigo_cuenta_detalle,
        nombre=nombre 
    )
    cuenta_detalle.save()
    return cuenta_detalle

#filtrado combobox
def get_rubros(request, tipo_id):
    rubros = RubroDeAgrupacion.objects.filter(idGrupoCuenta_id=tipo_id).values('idRubro', 'nombre')
    return JsonResponse(list(rubros), safe=False)

def get_cuentas_mayor(request, rubro_id):
    cuentas_mayor = CuentaDeMayor.objects.filter(idRubro_id=rubro_id).values('idDeMayor', 'nombre')
    return JsonResponse(list(cuentas_mayor), safe=False)

#funciones para usar en balance general y estado de capital

def obtener_info_empresa():
    info_empresa = Informacion.objects.first()  # Obtener la primera entrada
    return info_empresa.nombreEmpresa if info_empresa else "Nombre de la Empresa"

def obtener_fechas_periodo():
    periodo = PeriodoContable.objects.first()  # Ajusta esto según tu lógica
    if periodo:
        fecha_inicio = periodo.fechaInicioDePeriodo.strftime("%d de %B de %Y").lstrip('0').replace('  ', ' ')
        fecha_fin = periodo.fechaFinDePeriodo.strftime("%d de %B de %Y").lstrip('0').replace('  ', ' ')
        return fecha_inicio, fecha_fin
    return "Fecha de Inicio", "Fecha de Fin"


def balanceGeneral(request):
    # Obtener rubros específicos
    activo_corriente = RubroDeAgrupacion.objects.filter(nombre="ACTIVO CORRIENTE").first()
    activo_no_corriente = RubroDeAgrupacion.objects.filter(nombre="ACTIVO NO CORRIENTE").first()
    pasivo_corriente = RubroDeAgrupacion.objects.filter(nombre="PASIVO CORRIENTE").first()
    pasivo_no_corriente = RubroDeAgrupacion.objects.filter(nombre="PASIVO NO CORRIENTE").first()

    # Filtrar subcuentas y cuentas de detalle con transacciones con saldo distinto de cero
    transacciones_activo_corriente = Transacion.objects.filter(
    idSubCuenta__idDeMayor__idRubro=activo_corriente).exclude(idSubCuenta__idSubCuenta=6).values('idSubCuenta').annotate(
    saldo_absoluto=Abs(Sum('debe') - Sum('haber'))).filter(saldo_absoluto__gt=0)

    transacciones_detalle_activo_corriente = Transacion.objects.filter(idCuentaDetalle__idCuenta__idDeMayor__idRubro=activo_corriente).values('idCuentaDetalle').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)

    transacciones_activo_no_corriente = Transacion.objects.filter(idSubCuenta__idDeMayor__idRubro=activo_no_corriente).values('idSubCuenta').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)
    
    transacciones_detalle_activo_no_corriente = Transacion.objects.filter(idCuentaDetalle__idCuenta__idDeMayor__idRubro=activo_no_corriente).values('idCuentaDetalle').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)

    transacciones_pasivo_corriente = Transacion.objects.filter(idSubCuenta__idDeMayor__idRubro=pasivo_corriente).values('idSubCuenta').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)
    
    transacciones_detalle_pasivo_corriente = Transacion.objects.filter(idCuentaDetalle__idCuenta__idDeMayor__idRubro=pasivo_corriente).values('idCuentaDetalle').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)

    transacciones_pasivo_no_corriente = Transacion.objects.filter(idSubCuenta__idDeMayor__idRubro=pasivo_no_corriente).values('idSubCuenta').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)
    
    transacciones_detalle_pasivo_no_corriente = Transacion.objects.filter(idCuentaDetalle__idCuenta__idDeMayor__idRubro=pasivo_no_corriente).values('idCuentaDetalle').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    ).filter(saldo_absoluto__gt=0)



    # Filtrar subcuentas y cuentas de detalle basadas en las transacciones filtradas
    subcuentas_activo_corriente = SubCuenta.objects.filter(
    idSubCuenta__in=[t['idSubCuenta'] for t in transacciones_activo_corriente]).exclude(idSubCuenta=6)
    cuentas_detalle_activo_corriente = CuentaDetalle.objects.filter(idCuentaDetalle__in=[t['idCuentaDetalle'] for t in transacciones_detalle_activo_corriente])

    subcuentas_activo_no_corriente = SubCuenta.objects.filter(idSubCuenta__in=[t['idSubCuenta'] for t in transacciones_activo_no_corriente])
    cuentas_detalle_activo_no_corriente = CuentaDetalle.objects.filter(idCuentaDetalle__in=[t['idCuentaDetalle'] for t in transacciones_detalle_activo_no_corriente])

    subcuentas_pasivo_corriente = SubCuenta.objects.filter(idSubCuenta__in=[t['idSubCuenta'] for t in transacciones_pasivo_corriente])
    cuentas_detalle_pasivo_corriente = CuentaDetalle.objects.filter(idCuentaDetalle__in=[t['idCuentaDetalle'] for t in transacciones_detalle_pasivo_corriente])

    subcuentas_pasivo_no_corriente = SubCuenta.objects.filter(idSubCuenta__in=[t['idSubCuenta'] for t in transacciones_pasivo_no_corriente])
    cuentas_detalle_pasivo_no_corriente = CuentaDetalle.objects.filter(idCuentaDetalle__in=[t['idCuentaDetalle'] for t in transacciones_detalle_pasivo_no_corriente])

    # Recuperando el resultado del estado de capital y redondeándolo a dos decimales
    capitales_iniciales = request.session.get('capitales_iniciales', 0)
    capitales_iniciales = Decimal(capitales_iniciales).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    # Calcular sumas de saldos para activos y pasivo + capital
    total_activos = Decimal(sum(transaccion['saldo_absoluto'] for transaccion in transacciones_activo_corriente) + \
                sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_activo_corriente) + \
                sum(transaccion['saldo_absoluto'] for transaccion in transacciones_activo_no_corriente) + \
                sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_activo_no_corriente)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    total_pasivo_capital = Decimal(sum(transaccion['saldo_absoluto'] for transaccion in transacciones_pasivo_corriente) + \
                       sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_pasivo_corriente) + \
                       sum(transaccion['saldo_absoluto'] for transaccion in transacciones_pasivo_no_corriente) + \
                       sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_pasivo_no_corriente) + \
                       capitales_iniciales).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    
    
    # Obtener la información de la empresa y las fechas del periodo
    nombre_empresa = obtener_info_empresa()
    fecha_inicio, fecha_fin = obtener_fechas_periodo()

    # Combinar listas de subcuentas y cuentas de detalle por rubro
    subcuentas_corrientes = zip_longest(subcuentas_activo_corriente, subcuentas_pasivo_corriente)
    cuentas_detalle_corrientes = zip_longest(cuentas_detalle_activo_corriente, cuentas_detalle_pasivo_corriente)

    subcuentas_no_corrientes = zip_longest(subcuentas_activo_no_corriente, subcuentas_pasivo_no_corriente)
    cuentas_detalle_no_corrientes = zip_longest(cuentas_detalle_activo_no_corriente, cuentas_detalle_pasivo_no_corriente)
    
    

    context = {
        'subcuentas_corrientes': subcuentas_corrientes,
        'cuentas_detalle_corrientes': cuentas_detalle_corrientes,
        'subcuentas_no_corrientes': subcuentas_no_corrientes,
        'cuentas_detalle_no_corrientes': cuentas_detalle_no_corrientes,
        'transacciones_activo_corriente': transacciones_activo_corriente,
        'transacciones_detalle_activo_corriente': transacciones_detalle_activo_corriente,
        'transacciones_activo_no_corriente': transacciones_activo_no_corriente,
        'transacciones_detalle_activo_no_corriente': transacciones_detalle_activo_no_corriente,
        'transacciones_pasivo_corriente': transacciones_pasivo_corriente,
        'transacciones_detalle_pasivo_corriente': transacciones_detalle_pasivo_corriente,
        'transacciones_pasivo_no_corriente': transacciones_pasivo_no_corriente,
        'transacciones_detalle_pasivo_no_corriente': transacciones_detalle_pasivo_no_corriente,
        'nombre_empresa': nombre_empresa,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_activos': total_activos,
        'total_pasivo_capital': total_pasivo_capital,
        'capitales_iniciales': capitales_iniciales,
    }
    
    
    if request.GET.get('format') == 'pdf':
        # Renderizar el HTML como string
        html_string = render_to_string("App_innovaSoft/balanceGeneral.html", context)

        # Crear el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="balance_general.pdf"'
        pisa_status = pisa.CreatePDF(html_string, dest=response,encoding='utf-8')

        # Verificar si hubo un error al generar el PDF
        if pisa_status.err:
            return HttpResponse("Error al generar el PDF")

        return response
    
    return render(request, "App_innovaSoft/balanceGeneral.html", context)






def hojAjustes(request):
    return render(request,"App_innovaSoft/hojAjustes.html")

def estadoCapital(request):
    subcuenta_codigos = ['3202.01', '4202.01', '1103.01','3101.01','3101.02']
    cuenta_detalle_codigos = []

    subcuentas = SubCuenta.objects.filter(codigoCuenta__in=subcuenta_codigos)
    detalle_cuentas = CuentaDetalle.objects.filter(codigoCuenta__in=cuenta_detalle_codigos)


    # Obtener la información de la empresa y las fechas del periodo
    nombre_empresa = obtener_info_empresa()
    fecha_inicio, fecha_fin = obtener_fechas_periodo()


    # Obtenemos las transacciones y calculamos el saldo absoluto
    subcuenta_transacciones = Transacion.objects.filter(idSubCuenta__in=subcuentas).values('idSubCuenta').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    )

    cuenta_detalle_transacciones = Transacion.objects.filter(idCuentaDetalle__in=detalle_cuentas).values('idCuentaDetalle').annotate(
        saldo_absoluto=Abs(Sum('debe') - Sum('haber'))
    )

    cuentas_data = []
    saldo_3202_01 = 0  # Inicializamos para almacenar el saldo de 3202.01
    disminuciones_total = 0
    capitales_iniciales = 0
    # Clasificamos las subcuentas
    for subcuenta in subcuentas:
        transaccion = next(
            (item for item in subcuenta_transacciones if item['idSubCuenta'] == subcuenta.idSubCuenta),
            {'saldo_absoluto': 0}
        )

        # Clasificación de saldo según el tipo de cuenta
        if subcuenta.codigoCuenta == '1103.01':  # Disminuciones
            saldo_inicial = aumentos = 0
            disminuciones = transaccion['saldo_absoluto']
            disminuciones_total += disminuciones
        elif subcuenta.codigoCuenta == '3202.01':  # Saldo inicial
            saldo_inicial = transaccion['saldo_absoluto']
            saldo_3202_01 = saldo_inicial  # Guardamos el saldo para usar después
            aumentos = disminuciones = 0
        elif subcuenta.codigoCuenta == '4202.01':  # Aumentos
            saldo_inicial = aumentos = 0
            disminuciones = transaccion['saldo_absoluto']
            disminuciones_total += disminuciones
        elif subcuenta.codigoCuenta ==  '3101.01':  
            disminuciones = aumentos = 0
            saldo_inicial = transaccion['saldo_absoluto']
            capitales_iniciales += saldo_inicial
        elif subcuenta.codigoCuenta ==  '3101.02':  
            disminuciones = aumentos = 0
            saldo_inicial = transaccion['saldo_absoluto']     
            capitales_iniciales += saldo_inicial
        
        cuentas_data.append({
            'cuenta': subcuenta.nombre,
            'saldo_inicial': saldo_inicial,
            'aumentos': aumentos,
            'disminuciones': disminuciones
        })

    
    # Clasificamos las cuentas de detalle de manera similar, en el caso existan cuentas detalles que vayan a capital
    for cuenta_detalle in detalle_cuentas:
        transaccion = next(
            (item for item in cuenta_detalle_transacciones if item['idCuentaDetalle'] == cuenta_detalle.idCuentaDetalle),
            {'saldo_absoluto': 0}
        )

        if cuenta_detalle.codigoCuenta == '': 
            saldo_inicial = transaccion['saldo_absoluto']
            capitales_iniciales += saldo_inicial
            aumentos = disminuciones = 0
        elif cuenta_detalle.codigoCuenta == '': 
            aumentos = disminuciones = 0
            saldo_inicial = transaccion['saldo_absoluto']
            capitales_iniciales += saldo_inicial

           

        cuentas_data.append({
            'cuenta': cuenta_detalle.nombre,
            'saldo_inicial': saldo_inicial,
            'aumentos': aumentos,
            'disminuciones': disminuciones
        })
    
    
    # Aseguramos que el resultado final sea positivo
    total_final = saldo_3202_01 - disminuciones_total + capitales_iniciales
    total_final = abs(total_final)  # Convertimos a valor absoluto

    # Guardar capitales_iniciales en la sesión como float
    request.session['capitales_iniciales'] = float(total_final)  # Convertimos a float


   

    # Verificamos si se solicita un PDF
    if request.GET.get('format') == 'pdf':
        # Renderizamos el HTML en un string
        html_string = render_to_string('App_innovaSoft/estadoCapital.html', {
            'cuentas_data': cuentas_data,
            'total_final': total_final,
            'nombre_empresa': nombre_empresa,  # Pasamos el nombre de la empresa
            'fecha_inicio': fecha_inicio,       # Pasamos la fecha de inicio
            'fecha_fin': fecha_fin,             # Pasamos la fecha de fin
        })

        # Generamos el PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="estado_capital.pdf"'
        pisa_status = pisa.CreatePDF(html_string, dest=response)

        # Retornamos el PDF generado
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF')
        
        return response

    # Si no se solicita un PDF, no se devuelve nada
    return HttpResponse('No se puede generar el PDF, por favor verifica la solicitud.')



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


#METODO PARA VER EL LIBRO MAYOR
"METODO PARA VER EL LIBRO MAYOR"
def libro_mayor_view(request):
    # Agrupar transacciones por cuenta
    transacciones_por_cuenta = (
        Transacion.objects.values('idSubCuenta', 'idSubCuenta__nombre', 'idSubCuenta__codigoCuenta',
                                  'idCuentaDetalle', 'idCuentaDetalle__nombre', 'idCuentaDetalle__codigoCuenta')
        .annotate(
            total_debe=Sum('debe'),
            total_haber=Sum('haber'),
            saldo=Sum(F('debe') - F('haber'))
        )
        .order_by('idSubCuenta', 'idCuentaDetalle')
    )

    # Agregar lista de transacciones para cada cuenta en la lista `transacciones_por_cuenta`
    for cuenta in transacciones_por_cuenta:
        cuenta_id = cuenta['idSubCuenta'] or cuenta['idCuentaDetalle']
        cuenta['transacciones'] = Transacion.objects.filter(
            idSubCuenta=cuenta['idSubCuenta'] if cuenta['idSubCuenta'] else None,
            idCuentaDetalle=cuenta['idCuentaDetalle'] if cuenta['idCuentaDetalle'] else None
        ).select_related('idSubCuenta', 'idCuentaDetalle').order_by('idTransacion')

    return render(request, 'App_innovaSoft/libroMayor.html', {
        'transacciones_por_cuenta': transacciones_por_cuenta,
    })

#Guardar transacciones
@csrf_exempt
def save_transactions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transactions = data.get('transactions', [])
            last_id = Transacion.objects.order_by('-idTransacion').first()
            next_id = last_id.idTransacion + 1 if last_id else 1  # Start from 1 if no previous transactions

            # Start atomic transaction
            with transaction.atomic():
                for transaction_data in transactions:
                    cuenta_id = transaction_data['cuenta_id']
                    cuenta_id_type = transaction_data.get('cuenta_id_type')  # This new field indicates type
                    debe = transaction_data['debe']
                    haber = transaction_data['haber']

                    if cuenta_id_type == 'subcuenta':
                        try:
                            subcuenta = SubCuenta.objects.get(idSubCuenta=cuenta_id)
                            Transacion.objects.create(idTransacion=next_id, idSubCuenta=subcuenta, debe=debe, haber=haber)
                        except SubCuenta.DoesNotExist:
                            continue  # Skip invalid SubCuenta
                    elif cuenta_id_type == 'cuentadetalle':
                        try:
                            cuenta_detalle = CuentaDetalle.objects.get(idCuentaDetalle=cuenta_id)
                            Transacion.objects.create(idTransacion=next_id, idCuentaDetalle=cuenta_detalle, debe=debe, haber=haber)
                        except CuentaDetalle.DoesNotExist:
                            continue  # Skip invalid CuentaDetalle

                    next_id += 1  # Increment ID for next transaction

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print("Error al guardar transacciones:", e)  # Log error to console
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)


#METODO PARA VER LAS CUENTAS EN EL SELECT EN LA INTERFAZ DE TRANSACCIONES
def transaccion_view(request):
    # Obtener todas las subcuentas y sus cuentas de detalle
    subcuentas = SubCuenta.objects.prefetch_related('detalles').all()

    context = {
        'subcuentas_filtradas': subcuentas
    }
    return render(request, 'App_innovaSoft/transaccion.html', context)



#METODO PARA GENERAL EL BALANCE DE COMPROBACION
def generar_balance_de_comprobacion(request):
    # Crear el archivo PDF
    nombre_pdf = "balance_de_comprobacion.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_pdf}"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elementos = []

    # Configurar estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        alignment=1,  # Centrado
        fontSize=16,
        spaceAfter=12
    )
    sub_titulo_style = ParagraphStyle(
        "subtitulo",
        parent=styles["Normal"],
        alignment=1,  # Centrado
        fontSize=12,
        spaceAfter=12
    )

    # Obtener datos de la empresa e información del período
    info_empresa = Informacion.objects.first()
    nombre_empresa = info_empresa.nombreEmpresa if info_empresa else "Nombre de Empresa No Definido"

    periodo_contable = PeriodoContable.objects.first()
    fecha_inicio = periodo_contable.fechaInicioDePeriodo if periodo_contable else "Fecha Inicio No Definida"
    fecha_fin = periodo_contable.fechaFinDePeriodo if periodo_contable else "Fecha Fin No Definida"

    # Agregar nombre de la empresa como título
    titulo = Paragraph(f"{nombre_empresa}", titulo_style)
    elementos.append(titulo)

    # Agregar título del balance y fechas en una línea
    subtitulo = Paragraph("Balance de Comprobación", titulo_style)
    elementos.append(subtitulo)

    # Centrar las fechas en una sola línea
    fechas = Paragraph(f"Periodo: {fecha_inicio} - {fecha_fin}", sub_titulo_style)
    elementos.append(fechas)

    # Añadir un espacio antes de la tabla
    elementos.append(Spacer(1, 12))

    # Crear la tabla con datos de balance de comprobación
    datos = [["Código", "Cuenta", "Debe", "Haber"]]  # Encabezados de la tabla
    total_debe = 0
    total_haber = 0

    # Obtener transacciones y calcular totales
    transacciones = Transacion.objects.all()
    for transaccion in transacciones:
        cuenta_nombre = ""
        cuenta_codigo = ""
        
        if transaccion.idSubCuenta:
            cuenta_nombre = transaccion.idSubCuenta.nombre
            cuenta_codigo = transaccion.idSubCuenta.codigoCuenta
        elif transaccion.idCuentaDetalle:
            cuenta_nombre = transaccion.idCuentaDetalle.nombre
            cuenta_codigo = transaccion.idCuentaDetalle.codigoCuenta
        else:
            cuenta_nombre = "Cuenta desconocida"
            cuenta_codigo = "Código desconocido"
        
        # Valores de debe y haber
        debe = transaccion.debe
        haber = transaccion.haber
        datos.append([cuenta_codigo, cuenta_nombre, f"{debe:.2f}", f"{haber:.2f}"])
        total_debe += debe
        total_haber += haber

    # Agregar fila de totales
    datos.append(["", "Total", f"{total_debe:.2f}", f"{total_haber:.2f}"])

    # Crear la tabla en el PDF
    tabla = Table(datos, colWidths=[1.5 * inch, 2.5 * inch, 1.5 * inch, 1.5 * inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Fondo gris en encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elementos.append(tabla)

    # Construir el PDF
    doc.build(elementos)
    return response

#ESTADO DE RESULTADOS
def generar_estado_de_resultados(request):
    nombre_pdf = "estado_de_resultados.pdf"
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_pdf}"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elementos = []

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "titulo",
        parent=styles["Title"],
        alignment=1,
        fontSize=16,
        spaceAfter=12
    )
    sub_titulo_style = ParagraphStyle(
        "subtitulo",
        parent=styles["Normal"],
        alignment=1,
        fontSize=12,
        spaceAfter=12
    )

    info_empresa = Informacion.objects.first()
    nombre_empresa = info_empresa.nombreEmpresa if info_empresa else "Nombre de Empresa No Definido"
    periodo_contable = PeriodoContable.objects.first()
    fecha_inicio = periodo_contable.fechaInicioDePeriodo if periodo_contable else "Fecha Inicio No Definida"
    fecha_fin = periodo_contable.fechaFinDePeriodo if periodo_contable else "Fecha Fin No Definida"

    titulo = Paragraph(f"{nombre_empresa}", titulo_style)
    elementos.append(titulo)
    subtitulo = Paragraph("Estado de Resultados", titulo_style)
    elementos.append(subtitulo)
    fechas = Paragraph(f"Periodo: {fecha_inicio} - {fecha_fin}", sub_titulo_style)
    elementos.append(fechas)
    elementos.append(Spacer(1, 12))

    datos = [["Código", "Cuenta", "Saldo"]] 

    # Ingresos (Ventas Positivas)
    ingresos = 0
    cuentas_ingreso = ["5101.01"]  # Cuentas específicas de ingresos
    for codigo in cuentas_ingreso:
        transacciones = Transacion.objects.filter(idSubCuenta__codigoCuenta=codigo)
        saldo = sum(t.haber - t.debe for t in transacciones)  # Hacer ventas positivas
        ingresos += saldo

        cuenta_nombre = obtener_nombre_cuenta(codigo)
        datos.append([codigo, cuenta_nombre, f"{saldo:.2f}"])
    
    # Costos de Ventas
    costos_de_ventas = 0
    cuentas_costo_venta = ["5101.02", "4102.09", "4102.09.03", "4101.02", "4101.01"]

    for codigo in cuentas_costo_venta:
        transacciones = Transacion.objects.filter(idSubCuenta__codigoCuenta=codigo)
        saldo = sum(t.debe - t.haber for t in transacciones)
        costos_de_ventas += saldo

        cuenta_nombre = obtener_nombre_cuenta(codigo)
        datos.append([codigo, cuenta_nombre, f"{saldo:.2f}"])

    utilidad_bruta = ingresos - costos_de_ventas
    datos.append(["", "Utilidad Bruta", f"{utilidad_bruta:.2f}"])

    # Gastos Operativos (Agregar cuentas específicas)
    gastos_operativos = 0
    cuentas_gasto_operativo = ["4102.01.01", "4102.02", "4102.03", "4102.04", "4102.05", "4102.06", "4102.08", "4102.10", "4101.03", "4102.01.02", "4102.01.03", "4102.01.04", "4102.01.05", "4102.01.06", "4102.01.07", "4102.01.08", "4102.01.09", "4102.01.10", "4102.02.01", "4102.02.02", "4102.02.03", "4102.02.04", "4102.03.01", "4102.03.02", "4102.03.03", "4102.03.04", "4102.03.05", "4102.03.06", "4102.03.07", "4102.03.08", "4102.04.01", "4102.04.02", "4102.04.03", "4102.04.04", "4102.05.01", "4102.06.01", "4102.08.01", "4102.08.02","4102.08.03", "4102.08.04", "4102.08.05"]
    
    for codigo in cuentas_gasto_operativo:
        transacciones = Transacion.objects.filter(
        Q(idCuentaDetalle__codigoCuenta=codigo) | Q(idSubCuenta__codigoCuenta=codigo)
    )
        
        # Depuración intensiva
        print(f"\nCódigo: {codigo}")
        print(f"Total de transacciones encontradas: {transacciones.count()}")

        for t in transacciones:
            print(f"Debe: {t.debe}, Haber: {t.haber}")

        saldo = sum(t.debe - t.haber for t in transacciones)
        print(f"Saldo calculado para {codigo}: {saldo}")  # Imprime saldo calculado
        
        # Si el saldo es distinto de cero, se actualiza el total de gastos operativos
        gastos_operativos += saldo

        cuenta_nombre = obtener_nombre_cuenta(codigo)
        datos.append([codigo, cuenta_nombre, f"{saldo:.2f}"])
    
    utilidad_operativa = utilidad_bruta - gastos_operativos
    datos.append(["", "Utilidad Operativa", f"{utilidad_operativa:.2f}"])

    # Gastos Financieros
    gastos_financieros = 0
    cuentas_gasto_financiero = ["4102.07", "4201.01", "4201.02", "4102.07.01"]
    
    for codigo in cuentas_gasto_financiero:
        transacciones = Transacion.objects.filter(idSubCuenta__codigoCuenta=codigo)
        saldo = sum(t.debe - t.haber for t in transacciones)
        gastos_financieros += saldo

        cuenta_nombre = obtener_nombre_cuenta(codigo)
        datos.append([codigo, cuenta_nombre, f"{saldo:.2f}"])
    
    utilidad_antes_impuesto = utilidad_operativa - gastos_financieros
    datos.append(["", "Utilidad antes de Impuesto", f"{utilidad_antes_impuesto:.2f}"])

    # Impuesto y Utilidad Neta
    tasa_impuesto = Decimal(0.15)
    impuesto = utilidad_antes_impuesto * tasa_impuesto
    utilidad_neta = utilidad_antes_impuesto 
    registrar_utilidad_neta_y_perdidas(utilidad_neta)
    datos.append(["", "Impuesto (15%)", f"{impuesto:.2f}"])
    datos.append(["", "Utilidad Neta", f"{utilidad_neta:.2f}"])

    tabla = Table(datos, colWidths=[1.2 * inch, 3.5 * inch, 1.2 * inch])
    tabla.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
]))

    elementos.append(tabla)

    doc.build(elementos)
    return response

def obtener_nombre_cuenta(codigo_cuenta):
    """Obtiene el nombre de una cuenta desde SubCuenta o CuentaDetalle."""
    try:
        cuenta = SubCuenta.objects.get(codigoCuenta=codigo_cuenta)
        return cuenta.nombre
    except SubCuenta.DoesNotExist:
        pass

    try:
        cuenta_detalle = CuentaDetalle.objects.get(codigoCuenta=codigo_cuenta)
        return cuenta_detalle.nombre
    except CuentaDetalle.DoesNotExist:
        return ""
    
#METODO PARA GUARDAR LA UTILIDAD DESPUES DE DESCARGAR EL ESTADO DE RESULTADOS
def registrar_utilidad_neta_y_perdidas(utilidad_neta):
    """
    Registra la utilidad neta en la cuenta '3202.01' (Ejercicio Presente) y la cuenta '6101.01' (Pérdidas y Ganancias).
    Si la utilidad neta es positiva, se registra en el haber de 'Ejercicio Presente' y en el debe de 'Pérdidas y Ganancias'.
    Si es negativa, se registra en el debe de 'Ejercicio Presente' y en el haber de 'Pérdidas y Ganancias'.
    """
    valor_abs_utilidad_neta = abs(utilidad_neta)

    try:
        with transaction.atomic():
            # Buscar la última transacción en la tabla
            ultimo_id = Transacion.objects.latest('idTransacion').idTransacion if Transacion.objects.exists() else 0
            
            # Buscar las cuentas de ejercicio presente y pérdidas y ganancias
            cuenta_ejercicio_presente = SubCuenta.objects.get(codigoCuenta="3202.01")
            cuenta_perdidas_y_ganancias = SubCuenta.objects.get(codigoCuenta="6101.01")

            # Determinar los valores para cada cuenta
            debe_ejercicio = valor_abs_utilidad_neta if utilidad_neta < 0 else 0
            haber_ejercicio = valor_abs_utilidad_neta if utilidad_neta >= 0 else 0

            debe_perdidas = valor_abs_utilidad_neta if utilidad_neta >= 0 else 0
            haber_perdidas = valor_abs_utilidad_neta if utilidad_neta < 0 else 0

            # Crear o actualizar transacción en cuenta de ejercicio presente
            transaccion_ejercicio, created_ejercicio = Transacion.objects.update_or_create(
                idSubCuenta=cuenta_ejercicio_presente,
                defaults={'debe': debe_ejercicio, 'haber': haber_ejercicio},
                idTransacion=ultimo_id + 1
            )

            # Crear o actualizar transacción en cuenta de pérdidas y ganancias
            transaccion_perdidas, created_perdidas = Transacion.objects.update_or_create(
                idSubCuenta=cuenta_perdidas_y_ganancias,
                defaults={'debe': debe_perdidas, 'haber': haber_perdidas},
                idTransacion=ultimo_id + 2
            )

            print("Transacciones registradas o actualizadas exitosamente.")

    except SubCuenta.DoesNotExist as e:
        print(f"Error: No se encontró una cuenta necesaria: {e}")
    except Exception as e:
        print(f"Ocurrió un error al registrar las transacciones: {e}")




    


# Vistas CatalogoCuentas
def transaccion(request):
    CatalogoCuentas = SubCuenta.objects.all()  # Cambia a CuentaDetalle si quieres este nivel de detalle
    return render(request, 'App_innovaSoft/transaccion.html', {'CatalogoCuentas': CatalogoCuentas})

# Vistas CatalogoCuentas
def obtener_catalogo_cuentas(request):
    CatalogoCuentas = SubCuenta.objects.all()
    cuentas_json = [{"id": cuenta.idSubCuenta, "nombre": cuenta.nombre} for cuenta in CatalogoCuentas]
    return JsonResponse(cuentas_json, safe=False)


#inventario
def mostrar_activos(request):
    subcuentas_circulantes = SubCuenta.objects.filter(idDeMayor__idRubro__nombre='ACTIVO CORRIENTE').values('idSubCuenta', 'nombre')
    subcuentas_no_corrientes = SubCuenta.objects.filter(idDeMayor__idRubro__nombre='ACTIVO NO CORRIENTE').values('idSubCuenta', 'nombre')
    
    # Imprimir los datos para verificar en la consola
    print("Subcuentas Circulantes:", subcuentas_circulantes)
    print("Subcuentas No Corrientes:", subcuentas_no_corrientes)
    
    context = {
        'subcuentas_circulantes': subcuentas_circulantes,
        'subcuentas_no_corrientes': subcuentas_no_corrientes,
    }
    
    return render(request, 'App_innovaSoft/inventario.html', context)

#mostrar en tabla las transacciones de cada cuenta 
def obtener_transacciones(request):
    id_subcuenta = request.GET.get('idSubCuenta')
    
    if id_subcuenta:
        transacciones = Transacion.objects.filter(idSubCuenta_id=id_subcuenta).values('idSubCuenta__nombre', 'debe', 'haber')
        
        transacciones_list = []
        saldo = 0

        for transaccion in transacciones:
            saldo += transaccion['debe'] - transaccion['haber']
            transacciones_list.append({
                'nombre': transaccion['idSubCuenta__nombre'],
                'debe': float(transaccion['debe']),
                'haber': float(transaccion['haber']),
                'saldo': saldo
            })

        return JsonResponse({'transacciones': transacciones_list})
    else:
        return JsonResponse({'error': 'No se ha seleccionado una cuenta válida.'})



#calcular totales
def calcular_totales(request):
    # Inicializar los valores
    compras_totales = 0
    compras_netas = 0
    ventas_totales = 0
    ventas_netas = 0
    mercancias_disponibles = 0
    costo_ventas = 0
    perdidas_ganancia = 0

    # Definir códigos de cuenta para filtrar
    codigo_compras = "4102.09"
    codigo_gasto_compra = "4102.09.03"
    codigo_rebajas_compra = "4102.09.02"
    codigo_ventas = "5101.01"
    codigo_rebajas_venta = "5101.02"
    codigo_inventario_inicial = "1104.01"
    inventario_final = 1500  # Valor fijo dado

    # Obtener todas las transacciones
    transacciones = Transacion.objects.all()

    # Realizar cálculos basados en los códigos de cuenta
    for trans in transacciones:
        if trans.idSubCuenta and trans.idSubCuenta.codigoCuenta == codigo_compras:
            compras_totales += trans.debe - trans.haber
        elif trans.idSubCuenta and trans.idSubCuenta.codigoCuenta == codigo_gasto_compra:
            compras_totales += trans.debe - trans.haber
        elif trans.idSubCuenta and trans.idSubCuenta.codigoCuenta == codigo_rebajas_compra:
            compras_netas -= trans.debe - trans.haber
        elif trans.idSubCuenta and trans.idSubCuenta.codigoCuenta == codigo_ventas:
            ventas_totales += trans.haber - trans.debe
        elif trans.idSubCuenta and trans.idSubCuenta.codigoCuenta == codigo_rebajas_venta:
            ventas_netas -= trans.haber - trans.debe
        elif trans.idSubCuenta and trans.idSubCuenta.codigoCuenta == codigo_inventario_inicial:
            mercancias_disponibles += trans.debe - trans.haber

    # Finalizar cálculos
    compras_netas = compras_totales + compras_netas
    ventas_netas = ventas_totales + ventas_netas
    mercancias_disponibles += compras_netas
    costo_ventas = mercancias_disponibles - inventario_final
    perdidas_ganancia = ventas_netas - costo_ventas

    # Asegurar que los valores enviados sean numéricos
    return JsonResponse({
        'compras_totales': float(compras_totales or 0),
        'compras_netas': float(compras_netas or 0),
        'ventas_totales': float(ventas_totales or 0),
        'ventas_netas': float(ventas_netas or 0),
        'mercancias_disponibles': float(mercancias_disponibles or 0),
        'costo_ventas': float(costo_ventas or 0),
        'perdidas_ganancia': float(perdidas_ganancia or 0)
    })




