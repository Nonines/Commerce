# Generated by Django 4.1.1 on 2022-10-11 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="category",
            field=models.CharField(
                blank=True, default="No specified category", max_length=24, null=True
            ),
        ),
        migrations.AlterField(
            model_name="listing",
            name="image",
            field=models.URLField(blank=True, null=True),
        ),
    ]
