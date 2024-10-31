
from django.shortcuts import render,redirect
from .models import GrupoCuenta, RubroDeAgrupacion, CuentaDeMayor,SubCuenta,CuentaDetalle,Transacion,Informacion,PeriodoContable
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


def hojAjustes(request):
    return render(request,"App_innovaSoft/hojAjustes.html")

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




