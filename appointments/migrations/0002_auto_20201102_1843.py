# Generated by Django 3.0.7 on 2020-11-02 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='date',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='appointments',
            name='time',
            field=models.CharField(max_length=10),
        ),
    ]