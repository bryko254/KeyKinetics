# Generated by Django 5.1.4 on 2024-12-10 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0011_alter_vehicle_parking_spot'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='key',
            options={'verbose_name': 'Key', 'verbose_name_plural': 'Keys'},
        ),
        migrations.AlterModelOptions(
            name='keycheckout',
            options={'ordering': ['-checked_out_time'], 'verbose_name': 'Key Checkout', 'verbose_name_plural': 'Key Checkouts'},
        ),
        migrations.AlterField(
            model_name='keycheckout',
            name='checked_out_time',
            field=models.DateTimeField(),
        ),
    ]
