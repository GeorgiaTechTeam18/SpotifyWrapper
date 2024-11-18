# Generated by Django 5.1.2 on 2024-11-18 01:14

import uuid
from django.db import migrations, models

def gen_uuid(apps, schema_editor):
    MyModel = apps.get_model("Wrapped", "spotifywrap")
    for row in MyModel.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=["uuid"])

class Migration(migrations.Migration):

    dependencies = [
        ('Wrapped', '0004_spotifywrap_audio_features'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
