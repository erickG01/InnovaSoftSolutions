# Generated by Django 5.0.3 on 2024-10-26 16:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CuentaDeMayor',
            fields=[
                ('idDeMayor', models.AutoField(primary_key=True, serialize=False)),
                ('codigoCuenta', models.CharField(max_length=256, unique=True)),
                ('nombre', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'db_table': 'cuentaMayor',
                'ordering': ['idDeMayor'],
            },
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'db_table': 'departamento',
            },
        ),
        migrations.CreateModel(
            name='GrupoCuenta',
            fields=[
                ('idGrupoCuenta', models.AutoField(primary_key=True, serialize=False)),
                ('codigoGrupoCuenta', models.CharField(max_length=256, unique=True)),
                ('nombre', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'db_table': 'grupoCuenta',
                'ordering': ['idGrupoCuenta'],
            },
        ),
        migrations.CreateModel(
            name='Informacion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombreEmpresa', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'db_table': 'informacion',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Prestaciones',
            fields=[
                ('idPrestaciones', models.AutoField(primary_key=True, serialize=False)),
                ('tasaSeguro', models.DecimalField(decimal_places=4, max_digits=4)),
                ('tasaAFP', models.DecimalField(decimal_places=4, max_digits=4)),
                ('tasaIncaf', models.DecimalField(decimal_places=3, max_digits=4)),
                ('recargoPorVacaciones', models.DecimalField(decimal_places=3, max_digits=4)),
            ],
            options={
                'db_table': 'prestaciones',
                'ordering': ['idPrestaciones'],
            },
        ),
        migrations.CreateModel(
            name='RegistroCuentaT',
            fields=[
                ('idCuentaT', models.AutoField(primary_key=True, serialize=False)),
                ('debe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('haber', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'registroCuentaT',
                'ordering': ['idCuentaT'],
            },
        ),
        migrations.CreateModel(
            name='Cuenta',
            fields=[
                ('idCuenta', models.AutoField(primary_key=True, serialize=False)),
                ('codigoCuenta', models.CharField(max_length=256, unique=True)),
                ('nombre', models.CharField(max_length=256, unique=True)),
                ('idDeMayor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.cuentademayor')),
            ],
            options={
                'db_table': 'cuenta',
                'ordering': ['idCuenta'],
            },
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('idEmpleado', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=256, unique=True)),
                ('eficiencia', models.DecimalField(decimal_places=2, max_digits=2)),
                ('diasAguinaldo', models.IntegerField()),
                ('diasVacacion', models.IntegerField()),
                ('horasLaboradasDiarias', models.IntegerField()),
                ('salarioDiario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nDiasDeLaSemanaLabora', models.DecimalField(decimal_places=1, max_digits=2)),
                ('idDepartamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.departamento')),
                ('idPrestaciones', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.prestaciones')),
            ],
            options={
                'db_table': 'empleado',
                'ordering': ['idEmpleado'],
            },
        ),
        migrations.CreateModel(
            name='CostoReal',
            fields=[
                ('idCostoReal', models.AutoField(primary_key=True, serialize=False)),
                ('costoReal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('idEmpleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.empleado')),
            ],
            options={
                'db_table': 'costoReal',
                'ordering': ['idCostoReal'],
            },
        ),
        migrations.CreateModel(
            name='OrdenTrabajo',
            fields=[
                ('idOrden', models.AutoField(primary_key=True, serialize=False)),
                ('numeroOrden', models.IntegerField()),
                ('fechaInico', models.DateField()),
                ('fechaFin', models.DateField()),
                ('personal', models.TextField()),
                ('idCostoReal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.costoreal')),
                ('idDepartamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.departamento')),
            ],
            options={
                'db_table': 'ordenDeTrabajo',
                'ordering': ['idOrden'],
            },
        ),
        migrations.CreateModel(
            name='EstadoDeResultados',
            fields=[
                ('idEstadoDeResultados', models.AutoField(primary_key=True, serialize=False)),
                ('fechaDeElaboracion', models.DateField()),
                ('debe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('haber', models.DecimalField(decimal_places=2, max_digits=10)),
                ('UtilidadBruta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('UtilidadDeOperacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('UtilidadAntesDeOtrosIngresos', models.DecimalField(decimal_places=2, max_digits=10)),
                ('UtilidadAntesDeImpuesto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('UtilidadNeta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('idInformacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.informacion')),
                ('idCuentaT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.registrocuentat')),
            ],
            options={
                'db_table': 'estadoDeResultados',
                'ordering': ['idEstadoDeResultados'],
            },
        ),
        migrations.CreateModel(
            name='EstadoDeCapital',
            fields=[
                ('idEstadoCapital', models.AutoField(primary_key=True, serialize=False)),
                ('fechaDeElaboracion', models.DateField()),
                ('debe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('haber', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nuevoSaldo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('idInformacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.informacion')),
                ('idCuentaT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.registrocuentat')),
            ],
            options={
                'db_table': 'estadoDeCapital',
                'ordering': ['idEstadoCapital'],
            },
        ),
        migrations.CreateModel(
            name='BalanceGeneral',
            fields=[
                ('idBalanceGeneral', models.AutoField(primary_key=True, serialize=False)),
                ('fechaDeElaboracion', models.DateField()),
                ('debe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('haber', models.DecimalField(decimal_places=2, max_digits=10)),
                ('resultado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('idInformacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.informacion')),
                ('idCuentaT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.registrocuentat')),
            ],
            options={
                'db_table': 'balanceGeneral',
                'ordering': ['idBalanceGeneral'],
            },
        ),
        migrations.CreateModel(
            name='BalanceDeComprobacion',
            fields=[
                ('idBalanceDeComprobacion', models.AutoField(primary_key=True, serialize=False)),
                ('fechaDeElaboracion', models.DateField()),
                ('debe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('haber', models.DecimalField(decimal_places=2, max_digits=10)),
                ('resultado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('idInformacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.informacion')),
                ('idCuentaT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.registrocuentat')),
            ],
            options={
                'db_table': 'balanceDeComprobacion',
                'ordering': ['idBalanceDeComprobacion'],
            },
        ),
        migrations.CreateModel(
            name='RubroDeAgrupacion',
            fields=[
                ('idRubro', models.AutoField(primary_key=True, serialize=False)),
                ('codigoCuenta', models.CharField(max_length=256, unique=True)),
                ('nombre', models.CharField(max_length=256, unique=True)),
                ('idGrupoCuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.grupocuenta')),
            ],
            options={
                'db_table': 'rubroCuenta',
                'ordering': ['idRubro'],
            },
        ),
        migrations.AddField(
            model_name='cuentademayor',
            name='idRubro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.rubrodeagrupacion'),
        ),
        migrations.CreateModel(
            name='Transacion',
            fields=[
                ('idTransacion', models.AutoField(primary_key=True, serialize=False)),
                ('debe', models.DecimalField(decimal_places=2, max_digits=10)),
                ('haber', models.DecimalField(decimal_places=2, max_digits=10)),
                ('idCuenta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.cuenta')),
            ],
            options={
                'db_table': 'transacion',
                'ordering': ['idTransacion'],
            },
        ),
        migrations.AddField(
            model_name='registrocuentat',
            name='idTransacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.transacion'),
        ),
        migrations.CreateModel(
            name='LibroMayor',
            fields=[
                ('idLibroMayor', models.AutoField(primary_key=True, serialize=False)),
                ('fechaInicioDePeriodo', models.DateField()),
                ('fechaFinDePeriodo', models.DateField()),
                ('idTransacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App_innovaSoft.transacion')),
            ],
            options={
                'db_table': 'libroMayor',
                'ordering': ['idLibroMayor'],
            },
        ),
    ]
