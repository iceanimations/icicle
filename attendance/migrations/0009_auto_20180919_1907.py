# Generated by Django 2.1 on 2018-09-19 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_auto_20180919_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.IntegerField()),
                ('tid', models.IntegerField()),
                ('date', models.DateField(max_length=8)),
                ('time', models.TimeField(max_length=6)),
            ],
        ),
        migrations.AlterField(
            model_name='session',
            name='inTime',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='outTime',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]