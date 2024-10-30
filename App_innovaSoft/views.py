from django.shortcuts import render

# Crea tus vistas aquí.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")              # Renderiza la plantilla de inicio

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")          # Renderiza la plantilla del Libro Mayor

def CatalogoCuentas(request):
    return render(request,"App_innovaSoft/CatalogoCuentas.html")     # Renderiza la plantilla del Catálogo de Cuentas

def hojAjustes(request):
    return render(request,"App_innovaSoft/hojAjustes.html")          # Renderiza la plantilla de la Hoja de Ajustes