# Generated by Django 5.1.1 on 2024-10-08 14:37

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store_api", "0002_alter_user_deleted_alter_user_updated"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now_add=True)),
                ("deleted", models.DateTimeField(null=True)),
                ("title", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=1000)),
                ("price", models.IntegerField()),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("AVAILABLE", "Available"),
                            ("SOLD_OUT", "Sold Out"),
                            ("DELETED", "Deleted"),
                        ],
                        default="DRAFT",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("price__gt", 0)),
                        name="store_api_product_price_gt_zero",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="ProductStock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("variant", models.CharField(default="default")),
                ("available", models.IntegerField()),
                ("reserved", models.IntegerField()),
                ("sold", models.IntegerField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="store_api.product",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("variant", "product"),
                        name="store_api_productstock_unique_per_product_and_variant",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("available__gte", 0)),
                        name="store_api_productstock_available_gte_zero",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("reserved__gte", 0)),
                        name="store_api_productstock_reserved_gte_zero",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("sold__gte", 0)),
                        name="store_api_productstock_sold_gte_zero",
                    ),
                ],
            },
        ),
    ]
