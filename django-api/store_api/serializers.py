from rest_framework import serializers

from store_api.models import User

# TODO these are constants OR configurables that should be in settings.py for example
name_length = 50
username_length = 50
password_length = 50


class CreateUserRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=name_length)
    last_name = serializers.CharField(max_length=name_length)
    username = serializers.CharField(max_length=username_length)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=password_length)


class UpdateUserPasswordRequestSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=password_length)
    new_password = serializers.CharField(max_length=password_length)


class UserPublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "date_joined"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "date_joined", "first_name", "last_name", "email"]
