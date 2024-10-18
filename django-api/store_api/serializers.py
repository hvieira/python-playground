from rest_framework import serializers

from store_api.models import Product, User

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


class CreateProductRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=1000)
    price = serializers.IntegerField(min_value=1)
    available_stock = serializers.IntegerField(min_value=0)


class UpdateProductRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=1000)
    price = serializers.IntegerField(min_value=1)
    available_stock = serializers.IntegerField(min_value=0)


class UserPublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "date_joined"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "date_joined", "first_name", "last_name", "email"]


class ProductStockSerializer(serializers.RelatedField):
    def to_representation(self, value):
        # value is of type RelatedManager[ProductStock] and is defined at runtime
        return {
            s.variant: {
                "available": s.available,
                "reserved": s.reserved,
                "sold": s.sold,
            }
            for s in value.all()
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "description", "price", "stock", "owner_user_id"]

    stock = ProductStockSerializer(read_only=True)
