# Generated by Django 4.2.14 on 2024-08-19 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FETCH', '0010_datagenerationstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='datagenerationstatus',
            name='process_id',
            field=models.CharField(blank=True, null=True),
        ),
    ]
