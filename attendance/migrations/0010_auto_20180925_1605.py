# Generated by Django 2.1 on 2018-09-25 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0009_auto_20180919_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='entry',
            name='time',
            field=models.TimeField(),
        ),
    ]
