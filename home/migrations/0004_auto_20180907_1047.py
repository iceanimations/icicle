# Generated by Django 2.1 on 2018-09-07 05:47

from django.db import migrations, models
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20180906_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='photo',
            field=models.ImageField(blank=True, default='', upload_to=home.models.rename_photo),
        ),
    ]
