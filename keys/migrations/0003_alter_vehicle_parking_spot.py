# Generated by Django 5.1.4 on 2024-12-10 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0002_remove_vehicle_yard_section_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='parking_spot',
            field=models.CharField(blank=True, help_text="Location within the yard (e.g., 'A-12', 'Back Lot 5')", max_length=50, null=True),
        ),
    ]
