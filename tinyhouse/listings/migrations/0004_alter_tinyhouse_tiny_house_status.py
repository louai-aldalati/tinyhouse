# Generated by Django 5.2.1 on 2025-05-28 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0003_rename_status_tinyhouse_tiny_house_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tinyhouse',
            name='tiny_house_status',
            field=models.CharField(choices=[('beklemede', 'beklemede'), ('onayli', 'onayli'), ('iptal', 'iptal')], default='beklemede', max_length=10),
        ),
    ]
