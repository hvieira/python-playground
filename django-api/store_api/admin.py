from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from store_api.models import User

admin.site.register(User, UserAdmin)
