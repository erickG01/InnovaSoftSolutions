# Generated by Django 5.0.3 on 2024-10-29 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_innovaSoft', '0003_transacion_idcuentadetalle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuentadetalle',
            name='idCuenta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='App_innovaSoft.subcuenta'),
        ),
    ]
