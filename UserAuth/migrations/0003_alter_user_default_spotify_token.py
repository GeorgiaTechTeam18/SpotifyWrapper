# Generated by Django 5.1.2 on 2024-10-31 17:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAuth', '0002_spotifytoken_spotify_account_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='default_spotify_token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_spotify_token', to='UserAuth.spotifytoken'),
        ),
    ]
