# Generated by Django 2.1 on 2018-09-19 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_auto_20180919_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dayofshift',
            name='isTimeToNextDay',
            field=models.BooleanField(verbose_name='Crossing Date?'),
        ),
        migrations.AlterField(
            model_name='dayofshift',
            name='timeFrom',
            field=models.TimeField(verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='dayofshift',
            name='timeTo',
            field=models.TimeField(verbose_name='To'),
        ),
    ]