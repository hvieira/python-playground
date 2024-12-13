from datetime import datetime
from uuid import UUID

from django.contrib.auth.hashers import check_password
from django.db import transaction
from oauth2_provider.contrib.rest_framework import permissions as token_permissions
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from store_api.models import Product, Tag, User
from store_api.serializers import (
    CreateProductRequestSerializer,
    CreateUserRequestSerializer,
    ProductListSerializer,
    ProductSerializer,
    TagListSerializer,
    TagSerializer,
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

            with transaction.atomic():
                product.save()
                product.stock.create(
                    available=serializer.validated_data["available_stock"],
                    reserved=0,
                    sold=0,
                )

                if serializer.validated_data["tags"]:
                    for tag_id in serializer.validated_data["tags"]:
                        tag = Tag.objects.get(id=tag_id)
                        product.tags.add(tag)

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
            product.delete()
            product.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request: Request):
        page_size, offset = self._paging_params_from_request(request)
        results_queryset = self.queryset.order_by("-updated").all()

        if offset:
            results_queryset = results_queryset.filter(updated__lt=offset)

        serializer = ProductListSerializer(
            _list_and_paging_metadata(page_size, results_queryset, lambda p: p.updated)
        )
        return Response(serializer.data)

    def _paging_params_from_request(self, request: Request) -> tuple[int, datetime]:
        # TODO set these as "constants" somewhere
        default_page_size = 20

        page_size = int(request.query_params.get("page_size", default_page_size))
        # TODO is there any way to leverage Django or DRF to handle these query param transformations
        offset = request.query_params.get("offset", None)
        if offset:
            offset = datetime.fromisoformat(offset.replace("Z", "+00:00"))

        return page_size, offset


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.filter(deleted__isnull=True)
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        match self.action:
            case "list" | "retrieve":
                permission_classes = [permissions.IsAuthenticated]
            case _:
                permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

    def list(self, request: Request):
        # TODO set these as "constants" somewhere
        default_page_size = 50

        queryset = self.queryset.order_by("created")

        page_size = int(request.query_params.get("page_size", default_page_size))
        offset = request.query_params.get("offset", None)
        search_term = request.query_params.get("search_term", None)

        if search_term:
            queryset = queryset.filter(name__contains=search_term)

        if offset:
            offset = datetime.fromisoformat(offset.replace("Z", "+00:00"))
            queryset = queryset.filter(created__gt=offset)

        serializer = TagListSerializer(
            _list_and_paging_metadata(page_size, queryset, lambda t: t.created)
        )
        return Response(serializer.data)


# TODO probably can be integrated into a mixin or something to allow this paging to be re-used in all views and with less code
# perhaps based on this https://www.django-rest-framework.org/api-guide/pagination/#pagination
def _list_and_paging_metadata(page_size: int, queryset, offset_attribute_selector):
    total_results = queryset.all().count()
    paged = queryset[:page_size]
    results = list(paged)
    num_results = len(results)
    has_next = total_results > num_results

    return {
        "metadata": {
            "page_size": page_size,
            "offset_date": offset_attribute_selector(results[num_results - 1]),
            "has_next": has_next,
        },
        "data": results,
    }
