
from django.shortcuts import render,redirect
from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle,Transacion,Informacion,PeriodoContable,Transacion
from django.shortcuts import render,  redirect
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
from django.db.models import Sum, F, Func, Value
from django.db.models.functions import Abs
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import render_to_string
from itertools import zip_longest

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

    #Recuperando el resultado del estado de capital
    capitales_iniciales = request.session.get('capitales_iniciales', 0)
    # Convertir capitales_iniciales a Decimal
    capitales_iniciales = Decimal(capitales_iniciales)

    # Calcular sumas de saldos para activos y pasivo + capital
    total_activos = sum(transaccion['saldo_absoluto'] for transaccion in transacciones_activo_corriente) + \
                sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_activo_corriente) + \
                sum(transaccion['saldo_absoluto'] for transaccion in transacciones_activo_no_corriente) + \
                sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_activo_no_corriente)

    total_pasivo_capital = sum(transaccion['saldo_absoluto'] for transaccion in transacciones_pasivo_corriente) + \
                       sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_pasivo_corriente) + \
                       sum(transaccion['saldo_absoluto'] for transaccion in transacciones_pasivo_no_corriente) + \
                       sum(transaccion['saldo_absoluto'] for transaccion in transacciones_detalle_pasivo_no_corriente) + \
                       capitales_iniciales
    
    
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


    return render(request, "App_innovaSoft/balanceGeneral.html", context)




def hojAjustes(request):
    return render(request,"App_innovaSoft/hojAjustes.html")

def estadoCapital(request):
    subcuenta_codigos = ['3202.01', '4202.01', '1103.01','3101.01','3101.02']
    cuenta_detalle_codigos = []

    subcuentas = SubCuenta.objects.filter(codigoCuenta__in=subcuenta_codigos)
    detalle_cuentas = CuentaDetalle.objects.filter(codigoCuenta__in=cuenta_detalle_codigos)

    # Obtener la información general de la empresa
    info_empresa = Informacion.objects.first()  # Obtener la primera entrada
    nombre_empresa = info_empresa.nombreEmpresa if info_empresa else "Nombre de la Empresa"

    # Obtener el periodo contable
    periodo = PeriodoContable.objects.first()  # Ajusta esto según tu lógica
    fecha_inicio = periodo.fechaInicioDePeriodo.strftime("%d de %B de %Y").lstrip('0').replace('  ', ' ')
    fecha_fin = periodo.fechaFinDePeriodo.strftime("%d de %B de %Y").lstrip('0').replace('  ', ' ')

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
    request.session['capitales_iniciales'] = float(capitales_iniciales)  # Convertimos a float


   

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




