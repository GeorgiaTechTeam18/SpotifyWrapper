# Generated by Django 5.1.2 on 2024-10-23 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0002_alter_spotifytoken_access_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifytoken',
            name='refresh_token',
            field=models.CharField(max_length=150),
        ),
    ]
