from rest_framework import serializers

from store_api.models import Order, OrderLineItem, Product, Tag, User

# TODO these are constants OR configurables that should be in settings.py for example
name_length = 50
username_length = 50
password_length = 50


class UUIDListSerializer(serializers.ListSerializer):
    child = serializers.UUIDField()


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


class ProductStockSerializer(serializers.RelatedField):
    def to_representation(self, value):
        # value is of type RelatedManager[ProductStock] and is defined at runtime
        return {s.variant: s.available for s in value.all()}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "stock",
            "owner_user_id",
            "tags",
        ]

    tags = TagSerializer(many=True, read_only=True)
    stock = ProductStockSerializer(read_only=True)


class PagingMetadataSerializer(serializers.Serializer):
    page_size = serializers.IntegerField()
    offset_date = serializers.DateTimeField()
    has_next = serializers.BooleanField()


class ProductListSerializer(serializers.Serializer):
    metadata = PagingMetadataSerializer(read_only=True)
    data = ProductSerializer(many=True)


class TagListSerializer(serializers.Serializer):
    metadata = PagingMetadataSerializer(read_only=True)
    data = TagSerializer(many=True)


class CreateProductRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=1000)
    price = serializers.IntegerField(min_value=1)
    stock = serializers.DictField(
        child=serializers.IntegerField(min_value=0),
    )
    tags = UUIDListSerializer(required=False, default=[])


class UpdateProductRequestSerializer(CreateProductRequestSerializer):
    pass


class ProductInOrderSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    variant = serializers.CharField()
    quantity = serializers.IntegerField(min_value=0)


class CreateOrderRequestSerializer(serializers.Serializer):
    products = ProductInOrderSerializer(many=True)


class CreateOrderResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class OrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineItem
        fields = [
            "product_id",
            "variant",
            "quantity",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "state",
            "order_line_items",
        ]

    order_line_items = OrderLineItemSerializer(
        many=True, read_only=True, source="orderlineitem_set"
    )
