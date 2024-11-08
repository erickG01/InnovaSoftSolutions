from django.db import models

from django.contrib.auth.models import User

#Departamento
class Departamento(models.Model):
        idDepartamento=models.AutoField(primary_key=True),
        nombre=models.CharField(max_length=256,null=False,unique=True)

        def __str__(self):
            return self.nombre
        class Meta:
            db_table='departamento'
           
#Prestaciones
class Prestaciones(models.Model):
        idPrestaciones=models.AutoField(primary_key=True,null=False)
        tasaSeguro = models.DecimalField(max_digits=5, decimal_places=4, null=False) 
        tasaAFP = models.DecimalField(max_digits=5, decimal_places=4, null=False)     
        tasaIncaf = models.DecimalField(max_digits=3, decimal_places=2, null=False)   
        recargoPorVacaciones = models.DecimalField(max_digits=4, decimal_places=2, null=False)  
        
        def __str__(self):
            return self.nombre
        class Meta:
            db_table='prestaciones'
            ordering=['idPrestaciones']

#Empleado
class Empleado(models.Model):
     idEmpleado=models.AutoField(primary_key=True,null=False)
     idDepartamento=models.ForeignKey(Departamento,on_delete=models.CASCADE)
     idPrestaciones=models.ForeignKey(Prestaciones,on_delete=models.CASCADE)
     nombre=models.CharField(max_length=256,unique=True,null=False)
     eficiencia=models.DecimalField(max_digits=2,decimal_places=2)
     diasAguinaldo=models.IntegerField()
     diasVacacion=models.IntegerField()
     horasLaboradasDiarias=models.IntegerField()
     salarioDiario=models.DecimalField(max_digits=10,decimal_places=2)
     nDiasDeLaSemanaLabora=models.DecimalField(max_digits=2,decimal_places=1)

     def __str__(self):
            return self.nombre
     class Meta:
            db_table='empleado'
            ordering=['idEmpleado']

#Costo Real
class CostoReal(models.Model):
    idCostoReal=models.AutoField(primary_key=True,null=False)
    idEmpleado=models.ForeignKey(Empleado, on_delete=models.CASCADE)
    costoReal=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
            return self.nombre
    class Meta:
            db_table='costoReal'
            ordering=['idCostoReal']

#OrdenTrabajo
class OrdenTrabajo(models.Model):
      idOrden=models.AutoField( primary_key=True,null=False)
      idCostoReal=models.ForeignKey(CostoReal, on_delete=models.CASCADE)
      idDepartamento=models.ForeignKey(Departamento,on_delete=models.CASCADE)
      numeroOrden=models.IntegerField()
      fechaInico=models.DateField()
      fechaFin=models.DateField()
      personal=models.TextField()
      materiaPrima=models.TextField()
      costoManoDeObra=models.DecimalField(max_digits=10,decimal_places=2)
      costoMateriaPrima=models.DecimalField(max_digits=10,decimal_places=2)
      
      
      def __str__(self):
            return self.nombre
      class Meta:
            db_table='ordenDeTrabajo'
            ordering=['idOrden']

#GrupoCuenta
class GrupoCuenta(models.Model):
      idGrupoCuenta=models.AutoField(primary_key=True,null=False)
      codigoGrupoCuenta=models.CharField(max_length=256,unique=True)
      nombre=models.CharField(max_length=256,unique=True)

      def __str__(self):
            return self.nombre
      class Meta:
            db_table='grupoCuenta'
            ordering=['idGrupoCuenta']

#RubroCuenta
class RubroDeAgrupacion(models.Model):
      idRubro=models.AutoField(primary_key=True)
      idGrupoCuenta=models.ForeignKey(GrupoCuenta,on_delete=models.CASCADE)
      codigoCuenta=models.CharField(max_length=256,unique=True)
      nombre=models.CharField(max_length=256,unique=True)
      
      def __str__(self):
            return self.nombre
      class Meta:
            db_table='rubroCuenta'
            ordering=['idRubro']

#Cuenta Mayor
class CuentaDeMayor(models.Model):
      idDeMayor=models.AutoField(primary_key=True)
      idRubro=models.ForeignKey(RubroDeAgrupacion,on_delete=models.CASCADE)
      codigoCuenta=models.CharField(max_length=256,unique=True)
      nombre=models.CharField(max_length=256,unique=True)
     
      def __str__(self):
            return self.nombre
      class Meta:
            db_table='cuentaMayor'
            ordering=['idDeMayor']

#Cuenta
class SubCuenta(models.Model):
     idSubCuenta=models.AutoField(primary_key=True)
     idDeMayor=models.ForeignKey(CuentaDeMayor, on_delete=models.CASCADE)
     codigoCuenta=models.CharField(max_length=256,unique=True)
     nombre=models.CharField(max_length=256,unique=True)

     def __str__(self):
            return self.nombre
     class Meta:
            db_table='subCuenta'
            ordering=['idSubCuenta']

#Cuenta de detalle
class CuentaDetalle(models.Model):
     idCuentaDetalle=models.AutoField(primary_key=True)
     idCuenta=models.ForeignKey(SubCuenta, on_delete=models.CASCADE, related_name='detalles')
     codigoCuenta=models.CharField(max_length=256,unique=True)
     nombre=models.CharField(max_length=256,unique=True)

     def __str__(self):
            return self.nombre
     class Meta:
            db_table='cuentaDetalle'
            ordering=['idCuentaDetalle']

#Transacción
class Transacion(models.Model):
      idTransacion=models.AutoField(primary_key=True)
      idSubCuenta=models.ForeignKey(SubCuenta,on_delete=models.CASCADE,null=True)
      idCuentaDetalle=models.ForeignKey(CuentaDetalle,on_delete=models.CASCADE,null=True)
      debe=models.DecimalField(max_digits=10,decimal_places=2)
      haber=models.DecimalField(max_digits=10,decimal_places=2)

      def __str__(self):
            return self.nombre
      class Meta:
            db_table='transacion'
            ordering=['idTransacion']

#Registro en cuenta T
class RegistroCuentaT(models.Model):
        idCuentaT=models.AutoField(primary_key=True)
        idTransacion=models.ForeignKey(Transacion,on_delete=models.CASCADE)
        debe=models.DecimalField(max_digits=10,decimal_places=2)
        haber=models.DecimalField(max_digits=10,decimal_places=2)
        saldo=models.DecimalField(max_digits=10,decimal_places=2)
        def __str__(self):
            return self.nombre
        class Meta:
            db_table='registroCuentaT'
            ordering=['idCuentaT']

#Libro Mayor
class PeriodoContable(models.Model):
      idPeriodo=models.AutoField(primary_key=True)
      fechaInicioDePeriodo=models.DateField()
      fechaFinDePeriodo=models.DateField()
      
      def __str__(self):
            return self.nombre
      class Meta:
            db_table='periodoContable'
            ordering=['idPeriodo']

#Informacion General
class Informacion(models.Model):
      id=models.AutoField(primary_key=True)
      nombreEmpresa=models.CharField(max_length=256,unique=True)

      def __str__(self):
            return self.nombre
      class Meta:
            db_table='informacion'
            ordering=['id']

#Balance de comprobacion
class BalanceDeComprobacion(models.Model):
      idBalanceDeComprobacion=models.AutoField(primary_key=True)
      idInformacion=models.ForeignKey(Informacion,on_delete=models.CASCADE)
      idCuentaT=models.ForeignKey(RegistroCuentaT,on_delete=models.CASCADE)
      fechaDeElaboracion=models.DateField()
      debe=models.DecimalField(max_digits=10,decimal_places=2)
      haber=models.DecimalField(max_digits=10,decimal_places=2)
      resultado=models.DecimalField(max_digits=10,decimal_places=2)

      def __str__(self):
            return self.nombre
      class Meta:
            db_table='balanceDeComprobacion'
            ordering=['idBalanceDeComprobacion']

#Balance General
class BalanceGeneral(models.Model):
      idBalanceGeneral=models.AutoField(primary_key=True)
      idInformacion=models.ForeignKey(Informacion,on_delete=models.CASCADE)
      idCuentaT=models.ForeignKey(RegistroCuentaT,on_delete=models.CASCADE)
      fechaDeElaboracion=models.DateField()
      debe=models.DecimalField(max_digits=10,decimal_places=2)
      haber=models.DecimalField(max_digits=10,decimal_places=2)
      resultado=models.DecimalField(max_digits=10,decimal_places=2)

      def __str__(self):
            return self.nombre
      class Meta:
            db_table='balanceGeneral'
            ordering=['idBalanceGeneral']           

#Estado de capital
class EstadoDeCapital(models.Model):
      idEstadoCapital=models.AutoField(primary_key=True)
      idInformacion=models.ForeignKey(Informacion,on_delete=models.CASCADE)
      idCuentaT=models.ForeignKey(RegistroCuentaT,on_delete=models.CASCADE)
      fechaDeElaboracion=models.DateField()
      debe=models.DecimalField(max_digits=10,decimal_places=2)
      haber=models.DecimalField(max_digits=10,decimal_places=2)
      nuevoSaldo=models.DecimalField(max_digits=10,decimal_places=2)

      def __str__(self):
            return self.nombre
      class Meta:
            db_table='estadoDeCapital'
            ordering=['idEstadoCapital']    

#Estado de Resultados
class EstadoDeResultados(models.Model):
      idEstadoDeResultados=models.AutoField(primary_key=True)
      idInformacion=models.ForeignKey(Informacion,on_delete=models.CASCADE)
      idCuentaT=models.ForeignKey(RegistroCuentaT,on_delete=models.CASCADE)
      fechaDeElaboracion=models.DateField()
      debe=models.DecimalField(max_digits=10,decimal_places=2)
      haber=models.DecimalField(max_digits=10,decimal_places=2)
      UtilidadBruta=models.DecimalField(max_digits=10,decimal_places=2)
      UtilidadDeOperacion=models.DecimalField(max_digits=10,decimal_places=2)
      UtilidadAntesDeOtrosIngresos=models.DecimalField(max_digits=10,decimal_places=2) 
      UtilidadAntesDeImpuesto=models.DecimalField(max_digits=10,decimal_places=2)
      UtilidadNeta=models.DecimalField(max_digits=10,decimal_places=2)
        
      def __str__(self):
            return self.nombre
      class Meta:
            db_table='estadoDeResultados'
            ordering=['idEstadoDeResultados']   
class Producto(models.Model):
      idProducto=models.AutoField(primary_key=True)
      idSubCuenta=models.ForeignKey(SubCuenta,on_delete=models.CASCADE)
      nombre=models.CharField(max_length=256,unique=True)
      precio=models.DecimalField(max_digits=10, decimal_places=2)
      costo=models.DecimalField(max_digits=10,decimal_places=2,null=True)