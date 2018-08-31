# Generated by Django 2.1 on 2018-08-17 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0001_initial'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavetype',
            name='availability',
            field=models.ManyToManyField(to='home.EmployeeType'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='approvedBy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Employee'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='attendance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Attendance'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='leaveType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.LeaveType'),
        ),
        migrations.AddField(
            model_name='inout',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Employee'),
        ),
        migrations.AddField(
            model_name='dayofweekend',
            name='day',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Day'),
        ),
        migrations.AddField(
            model_name='dayofweekend',
            name='weekend',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.Weekend'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.Employee'),
        ),
    ]