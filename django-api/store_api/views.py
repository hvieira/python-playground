from uuid import UUID

from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from oauth2_provider.contrib.rest_framework import permissions as token_permissions
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from store_api.models import Product, User
from store_api.serializers import (
    CreateProductRequestSerializer,
    CreateUserRequestSerializer,
    ProductSerializer,
    UpdateProductRequestSerializer,
    UpdateUserPasswordRequestSerializer,
    UserProfileSerializer,
    UserPublicProfileSerializer,
)


class UserViewSet(GenericViewSet):
    lookup_field = "id"
    lookup_value_converter = "uuid"

    queryset = User.objects.all().filter(deleted__isnull=True)
    required_alternate_scopes = {
        "GET": [["read"]],
        "POST": [["write"]],
    }

    def get_permissions(self):
        match self.action:
            case "create":
                permission_classes = [permissions.AllowAny]
            case "retrieve":
                permission_classes = [token_permissions.TokenMatchesOASRequirements]
            case _:
                permission_classes = [token_permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request: Request):
        serializer = CreateUserRequestSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create_user(**serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request: Request, id: UUID = None):
        if request.user.id == id:
            serializer = UserProfileSerializer(request.user)
        else:
            wanted_user = self.queryset.get(id=id)
            serializer = UserPublicProfileSerializer(wanted_user)

        return Response(serializer.data)

    @action(
        url_path="update-password",
        detail=True,
        permission_classes=[token_permissions.TokenMatchesOASRequirements],
        methods=["post"],
    )
    def update_password(self, request: Request, id: UUID = None):
        serializer = UpdateUserPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        authenticated_user: User = request.user
        path_user: User = self.queryset.get(id=id)

        if not path_user or path_user.id != authenticated_user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if check_password(
            serializer.validated_data["old_password"], authenticated_user.password
        ):
            authenticated_user.set_password(serializer.validated_data["new_password"])
            authenticated_user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(GenericViewSet):
    lookup_field = "id"
    lookup_value_converter = "uuid"

    queryset = Product.objects.all().filter(deleted__isnull=True)
    required_alternate_scopes = {
        "GET": [["read"]],
        "POST": [["write"]],
        "PUT": [["write"]],
        "DELETE": [["write"]],
    }

    serializer_class = ProductSerializer

    def get_permissions(self):
        match self.action:
            case _:
                permission_classes = [token_permissions.TokenMatchesOASRequirements]

        return [permission() for permission in permission_classes]

    def create(self, request: Request):
        serializer = CreateProductRequestSerializer(data=request.data)
        if serializer.is_valid():
            product = Product(
                title=serializer.validated_data["title"],
                description=serializer.validated_data["description"],
                price=serializer.validated_data["price"],
                owner_user=request.user,
            )

            product.save()
            product.stock.create(
                available=serializer.validated_data["available_stock"],
                reserved=0,
                sold=0,
            )

            response_serializer = self.serializer_class(product)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, id: UUID = None):
        serializer = UpdateProductRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            product = self.queryset.get(id=id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if product.owner_user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        product.title = serializer.validated_data["title"]
        product.description = serializer.validated_data["description"]
        product.price = serializer.validated_data["price"]

        with transaction.atomic():
            product.stock.filter(variant="default").update(
                available=serializer.validated_data["available_stock"]
            )
            product.save()

        response_serializer = self.serializer_class(product)
        return Response(response_serializer.data)

    def destroy(self, request: Request, id: UUID = None):
        # TODO DRY get_or_404 properties
        # TODO can the out-of-the-box viewset mixins be configured
        # with appropriate serializers and resource creation to replace duplicated code
        try:
            product = self.queryset.get(id=id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if product.owner_user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            # stock of a deleted product is hard deleted to save space
            # if an undelete operation is to be supported, it needs to restore the default variant in stock
            product.stock.all().delete()
            product.deleted = timezone.now()
            product.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
