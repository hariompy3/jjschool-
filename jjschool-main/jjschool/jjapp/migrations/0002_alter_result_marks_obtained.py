# Generated by Django 5.0.6 on 2024-06-29 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jjapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="result",
            name="marks_obtained",
            field=models.FloatField(default=0),
        ),
    ]
