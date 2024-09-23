import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseEntity(models.Model):
    class Meta:
       abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated = models.DateTimeField(null=False, auto_now_add=True)
    deleted = models.DateTimeField(null=True)


class User(AbstractUser, BaseEntity):
    pass


class UserAPIToken(models.Model):
    token = models.CharField(primary_key=True, max_length=100, editable=False)
    user = models.ForeignKey(to=User, null=False, on_delete=models.DO_NOTHING ,editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    expiry = models.DateTimeField(null=False, editable=False)

