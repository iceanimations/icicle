# Generated by Django 2.1 on 2018-10-08 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0016_auto_20181008_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaverequest',
            name='approvalDate',
            field=models.DateTimeField(null=True),
        ),
    ]
