# Generated by Django 4.2.14 on 2024-08-28 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FETCH', '0006_cropdetails_process_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cropdatajson',
            name='added_time',
            field=models.DateTimeField(blank=True, max_length=255, null=True),
        ),
    ]
