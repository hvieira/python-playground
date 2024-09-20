import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseEntity(models.Model):
    class Meta:
       abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now_add=True)
    deleted = models.DateTimeField(null=True)


class User(AbstractUser, BaseEntity):
    pass
