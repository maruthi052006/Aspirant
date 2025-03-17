# Generated by Django 5.1.7 on 2025-03-08 06:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_remove_clg_source_name_clg_course_name"),
        ("trainer", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trainer",
            name="clg",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trainer",
                to="main.clg",
            ),
        ),
    ]
