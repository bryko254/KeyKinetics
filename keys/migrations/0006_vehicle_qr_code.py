# Generated by Django 5.1.4 on 2024-12-10 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0005_alter_keycheckout_purpose'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
    ]
