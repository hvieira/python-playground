# Generated by Django 5.1.1 on 2024-10-18 14:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store_api", "0003_product_productstock"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="owner_user",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="productstock",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="stock",
                to="store_api.product",
            ),
        ),
    ]
