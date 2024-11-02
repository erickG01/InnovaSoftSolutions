from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.shortcuts import render,  redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Sum, F
from django.db.models import Q
from django.db.models.functions import Abs
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from xhtml2pdf import pisa

from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle,Transacion,Informacion,PeriodoContable

from decimal import Decimal
from io import BytesIO
import json

# Crea tus vistas aquí.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")                 # Renderiza la plantilla de inicio

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")             # Renderiza la plantilla del Libro Mayor

def Costos(request):
    return render(request,"App_innovaSoft/costos.html")

def hojAjustes(request):
    return render(request,"App_innovaSoft/hojAjustes.html")

def estadoFinancieros(request):
    return render(request, 'App_innovaSoft/estadoFinancieros.html')     # Renderiza la plantilla de estados financieros

#def CatalogoCuentas(request):
 #   return render(request,"App_innovaSoft/CatalogoCuentas.html")

#Vistas CatalogoCuentas
def transaccion(request):
    return render(request,"App_innovaSoft/transaccion.html")

# Vistas CatalogoCuentas
def obtener_catalogo_cuentas(request):
    CatalogoCuentas = SubCuenta.objects.all()
    cuentas_json = [{"id": cuenta.idSubCuenta, "nombre": cuenta.nombre} for cuenta in CatalogoCuentas]
    return JsonResponse(cuentas_json, safe=False)

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

#METODO PARA EL LOGIN
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

# METODO PARA VER EL LIBRO MAYOR
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
    utilidad_neta = utilidad_antes_impuesto - impuesto
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
    
def estadoCapital(request):
    subcuenta_codigos = ['3202.01', '4202.01', '1103.01']
    cuenta_detalle_codigos = ['3101.01.01', '3101.02.01']

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
        
        cuentas_data.append({
            'cuenta': subcuenta.nombre,
            'saldo_inicial': saldo_inicial,
            'aumentos': aumentos,
            'disminuciones': disminuciones
        })

    capitales_iniciales = 0
    # Clasificamos las cuentas de detalle de manera similar
    for cuenta_detalle in detalle_cuentas:
        transaccion = next(
            (item for item in cuenta_detalle_transacciones if item['idCuentaDetalle'] == cuenta_detalle.idCuentaDetalle),
            {'saldo_absoluto': 0}
        )

        if cuenta_detalle.codigoCuenta == '3101.01.01': 
            saldo_inicial = transaccion['saldo_absoluto']
            capitales_iniciales += saldo_inicial
            aumentos = disminuciones = 0
        elif cuenta_detalle.codigoCuenta == '3101.02.01': 
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

# Vistas CatalogoCuentas
def transaccion(request):
    CatalogoCuentas = SubCuenta.objects.all()  # Cambia a CuentaDetalle si quieres este nivel de detalle
    return render(request, 'App_innovaSoft/transaccion.html', {'CatalogoCuentas': CatalogoCuentas})