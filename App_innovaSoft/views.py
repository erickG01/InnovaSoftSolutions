from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request,"App_innovaSoft/inicio.html")

def libroMayor(request):
    return render(request,"App_innovaSoft/libroMayor.html")

def CatalogoCuentas(request):
    return render(request,"App_innovaSoft/CatalogoCuentas.html")

def Costos(request):
    return render(request,"App_innovaSoft/costos.html")