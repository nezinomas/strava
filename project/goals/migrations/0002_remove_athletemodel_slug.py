# Generated by Django 5.0.4 on 2024-04-29 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("goals", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="athletemodel",
            name="slug",
        ),
    ]
