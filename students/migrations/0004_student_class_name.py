# Generated by Django 5.1.6 on 2025-03-02 00:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0003_attendance"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="class_name",
            field=models.CharField(
                blank=True, default="Not Assigned", max_length=50, null=True
            ),
        ),
    ]
