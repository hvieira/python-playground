# Generated by Django 5.1.3 on 2024-11-21 16:35

import django_fsm
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store_api", "0005_alter_product_owner_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="state",
            field=django_fsm.FSMField(
                choices=[
                    ("DRAFT", "Draft"),
                    ("AVAILABLE", "Available"),
                    ("SOLD_OUT", "Sold Out"),
                    ("DELETED", "Deleted"),
                ],
                default="DRAFT",
                max_length=50,
            ),
        ),
    ]
