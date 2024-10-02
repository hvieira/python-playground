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
