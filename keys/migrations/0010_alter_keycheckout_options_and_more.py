# Generated by Django 5.1.4 on 2024-12-10 15:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0009_alter_keycheckout_authorized_by_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='keycheckout',
            options={'ordering': ['-checked_out_time']},
        ),
        migrations.AlterField(
            model_name='keycheckout',
            name='checked_out_time',
            field=models.DateTimeField(default=django.utils.timezone.localtime),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='parking_spot',
            field=models.CharField(default='aaa', help_text="Location within the yard (e.g., 'A-12', 'Back Lot 5')", max_length=50),
            preserve_default=False,
        ),
    ]
