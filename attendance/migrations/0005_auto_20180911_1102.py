# Generated by Django 2.1 on 2018-09-11 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_employeeshift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeshift',
            name='dateTo',
            field=models.DateField(null=True, verbose_name='To'),
        ),
    ]