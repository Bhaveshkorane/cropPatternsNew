# Generated by Django 4.2.14 on 2024-08-20 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FETCH', '0014_remove_cropdatajson_added_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('process_id', models.CharField(blank=True, null=True)),
                ('crop', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_generation', models.BooleanField(default=False)),
                ('is_extraction', models.BooleanField(default=False)),
                ('is_aggregation', models.BooleanField(default=False)),
                ('is_failed', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='DataGenerationStatus',
        ),
        migrations.AddField(
            model_name='cropdatajson',
            name='is_failed',
            field=models.BooleanField(default=False),
        ),
    ]
