# Generated by Django 2.1 on 2018-09-19 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_auto_20180912_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='weekend',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='weekend',
        ),
    ]
