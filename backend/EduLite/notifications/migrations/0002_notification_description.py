# Generated by Django 5.2.1 on 2025-06-24 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
