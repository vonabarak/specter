# Generated by Django 3.2.4 on 2021-06-09 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_auto_20210609_2021"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="name",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]
