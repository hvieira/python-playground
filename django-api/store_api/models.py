import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseEntity(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated = models.DateTimeField(null=False, auto_now_add=True)
    deleted = models.DateTimeField(null=True)


class User(AbstractUser, BaseEntity):

    def save(self, **kwargs):
        self._validate_pre_save()
        super().save(**kwargs)

    def _validate_pre_save(self):
        if self.deleted and self.is_active:
            # TODO create a custom error for this
            raise RuntimeError("A deleted user cannot be active")


class Product(BaseEntity):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="%(app_label)s_%(class)s_price_gt_zero",
            )
        ]

    title = models.CharField(null=False, max_length=100)
    description = models.CharField(null=False, max_length=1000)
    price = models.IntegerField(null=False)

    def save(self, **kwargs):
        self._validate_pre_save()
        super().save(**kwargs)


class ProductStock(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(available__gte=0),
                name="%(app_label)s_%(class)s_available_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(reserved__gte=0),
                name="%(app_label)s_%(class)s_reserved_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(sold__gte=0),
                name="%(app_label)s_%(class)s_sold_gte_zero",
            ),
        ]

    id = None
    available = models.IntegerField(null=False)
    reserved = models.IntegerField(null=False)
    sold = models.IntegerField(null=False)
