# Generated by Django 2.1 on 2018-10-16 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0018_auto_20181011_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavetype',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
