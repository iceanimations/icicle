# Generated by Django 2.1 on 2018-08-17 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Department')),
                ('shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Shift')),
            ],
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50)),
                ('fatherName', models.CharField(max_length=50, verbose_name="Father's Name")),
                ('dob', models.DateField(verbose_name='Date of Birth')),
                ('joinDate', models.DateField(verbose_name='Joining Date')),
                ('address', models.CharField(blank=True, max_length=200)),
                ('photo', models.ImageField(blank=True, upload_to='')),
                ('isActive', models.BooleanField(default=True)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('mobile', models.CharField(blank=True, max_length=15)),
                ('cnic', models.CharField(blank=True, max_length=13)),
                ('dept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.Department')),
                ('designation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Designation')),
                ('shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Shift')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20, verbose_name='Employee Type')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('dateStart', models.DateField(verbose_name='Start Date')),
                ('dateEnd', models.DateField(blank=True, null=True, verbose_name='End Date')),
                ('active', models.BooleanField()),
                ('thumb', models.ImageField(blank=True, upload_to='', verbose_name='Thumbnail')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Employee')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.EmployeeType'),
        ),
        migrations.AddField(
            model_name='employee',
            name='weekend',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Weekend'),
        ),
        migrations.AddField(
            model_name='department',
            name='supervisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Employee'),
        ),
        migrations.AddField(
            model_name='department',
            name='weekend',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Weekend'),
        ),
    ]
