# Generated by Django 2.1 on 2018-10-23 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodOrder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodorder',
            name='approvalTime',
            field=models.DateTimeField(null=True),
        ),
    ]
