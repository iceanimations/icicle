# Generated by Django 2.1 on 2018-10-24 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodOrder', '0003_auto_20181023_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='isActive',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
        migrations.AlterField(
            model_name='foodorder',
            name='status',
            field=models.CharField(choices=[('served', 'Served'), ('cancelled', 'Cancelled'), ('rejected', 'Rejected'), ('pending', 'Pending'), ('placed', 'Placed')], default='placed', max_length=15),
        ),
    ]
