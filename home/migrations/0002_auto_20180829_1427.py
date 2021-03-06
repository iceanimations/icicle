# Generated by Django 2.1 on 2018-08-29 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='cnic',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='dob',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Birth'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='fatherName',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name="Father's Name"),
        ),
        migrations.AlterField(
            model_name='employee',
            name='isActive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='employee',
            name='joinDate',
            field=models.DateField(blank=True, null=True, verbose_name='Joining Date'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='mobile',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='photo',
            field=models.ImageField(upload_to=''),
        ),
    ]
