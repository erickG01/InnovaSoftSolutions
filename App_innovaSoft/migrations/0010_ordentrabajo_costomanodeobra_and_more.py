# Generated by Django 5.0.3 on 2024-11-04 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_innovaSoft', '0009_ordentrabajo_materiaprima_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordentrabajo',
            name='costoManoDeObra',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ordentrabajo',
            name='costoMateriaPrima',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
