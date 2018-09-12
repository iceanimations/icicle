# Generated by Django 2.1 on 2018-09-07 08:58

from django.db import migrations, models
import home.models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20180907_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='designation',
            name='title',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='cnic',
            field=models.CharField(blank=True, max_length=13, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='code',
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='mobile',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='photo',
            field=models.ImageField(blank=True, upload_to=home.models.rename_photo),
        ),
        migrations.AlterField(
            model_name='employee',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='employeedepartment',
            name='dateFrom',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='employeetype',
            name='type',
            field=models.CharField(max_length=20, unique=True, verbose_name='Employee Type'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]