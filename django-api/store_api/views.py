from datetime import datetime
from functools import reduce
from typing import Any, Callable
from uuid import UUID

import django_fsm
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.db.models import Q
from oauth2_provider.contrib.rest_framework import permissions as token_permissions
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from store_api.models import Order, OrderLineItem, Product, ProductStock, Tag, User
from store_api.serializers import (
    CreateOrderRequestSerializer,
    CreateOrderResponseSerializer,
    CreateProductRequestSerializer,
    CreateUserRequestSerializer,
    OrderSerializer,
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
            with transaction.atomic():
                product = Product(
                    title=serializer.validated_data["title"],
                    description=serializer.validated_data["description"],
                    price=serializer.validated_data["price"],
                    owner_user=request.user,
                )
                product.save()

                # TODO check serializer.stock.get_value() function
                stock_spec: dict = serializer.validated_data["stock"]
                # TODO this can probably be achieved with bulk create for a single DB call
                for variant, stock in stock_spec.items():
                    product.stock.create(
                        variant=variant,
                        available=stock,
                    )

                product.tags.set(
                    Tag.objects.filter(id__in=serializer.validated_data["tags"])
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
            product = self.queryset.select_for_update().get(id=id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if product.owner_user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        product.title = serializer.validated_data["title"]
        product.description = serializer.validated_data["description"]
        product.price = serializer.validated_data["price"]

        with transaction.atomic():
            # RelatedManager .set() function relies on remove() and clear() functions, which are only available
            # on relationships with ForeignKeys where null=True
            # https://docs.djangoproject.com/en/5.1/ref/models/relations/#django.db.models.fields.related.RelatedManager.clear
            ProductStock.objects.filter(product_id=product.id).delete()
            ProductStock.objects.bulk_create(
                [
                    ProductStock(product=product, variant=variant, available=stock)
                    for variant, stock in serializer.validated_data["stock"].items()
                ]
            )

            product.tags.set(
                Tag.objects.filter(id__in=serializer.validated_data["tags"])
            )

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
        search_term = request.query_params.get("search_term", None)

        if search_term:
            # note: without the distinct, the query will result in duplicated records
            # https://stackoverflow.com/questions/18071572/django-duplicates-when-filtering-on-many-to-many-field
            results_queryset = results_queryset.filter(
                Q(title__contains=search_term)
                | Q(description__contains=search_term)
                | Q(tags__name__contains=search_term)
            ).distinct()

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


class IsOwner(BasePermission):
    def __init__(self, retrieve_object_owner: Callable[[Any], User]):
        self.retrieve_object_owner = retrieve_object_owner

    def has_object_permission(self, request, view, obj: Order):
        object_owner = self.retrieve_object_owner(obj)
        return object_owner == request.user


class OrderViewSet(ModelViewSet):
    lookup_field = "id"
    lookup_value_converter = "uuid"

    order_owner_retriever: Callable[[Order], User] = lambda order: order.customer

    queryset = (
        Order.objects.all()
        .filter(deleted__isnull=True)
        .prefetch_related("orderlineitem_set")
    )

    serializer_class = OrderSerializer

    required_alternate_scopes = {
        "GET": [["read"]],
        "POST": [["write"]],
    }

    def get_permissions(self):
        match self.action:
            case "retrieve" | "list":
                permissions = [
                    token_permissions.TokenMatchesOASRequirements(),
                    IsOwner(self.order_owner_retriever),
                ]
            case _:
                permissions = [token_permissions.TokenMatchesOASRequirements()]

        return permissions
        # return [permission() for permission in permission_classes]

    def create(self, request: Request):
        serializer = CreateOrderRequestSerializer(data=request.data)
        if serializer.is_valid():
            requested_quantity_by_product_id_and_variant = {
                (p["id"], p["variant"]): p["quantity"]
                for p in serializer.validated_data["products"]
            }

            stock_queryset = (
                ProductStock.objects.filter(product__deleted__isnull=True)
                .select_for_update()
                .prefetch_related("product")
            )
            lookups = [
                Q(product_id=requested_product["id"])
                & Q(variant=requested_product["variant"])
                for requested_product in serializer.validated_data["products"]
            ]
            combined_lookup = reduce(lambda lu, acc: acc | lu, lookups)

            with transaction.atomic():
                processed_order_line_items = []
                order = Order.objects.create(customer=request.user)
                requested_products_stock = stock_queryset.filter(combined_lookup)

                if len(requested_products_stock) != len(
                    serializer.validated_data["products"]
                ):
                    missing_product_ids = set(
                        requested_quantity_by_product_id_and_variant.keys()
                    ).difference(
                        set(
                            [
                                (ps.product.id, ps.variant)
                                for ps in requested_products_stock
                            ]
                        )
                    )
                    return Response(
                        {
                            "error": "requested products and/or stock variants that do not exist",
                            "detail": missing_product_ids,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for product_stock in requested_products_stock:
                    requested_quantity = requested_quantity_by_product_id_and_variant[
                        (product_stock.product.id, product_stock.variant)
                    ]

                    product_stock.available -= requested_quantity

                    # we could let this go to the DB for constraint validation, but we can save that roundtrip
                    if product_stock.available < 0:
                        return Response(
                            {
                                "error": f"available stock for product {product_stock.product.id} is less than desired amount"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    processed_order_line_items.append(
                        OrderLineItem(
                            order=order,
                            product=product_stock.product,
                            variant=product_stock.variant,
                            quantity=requested_quantity,
                        )
                    )

                ProductStock.objects.bulk_update(
                    requested_products_stock, fields=["available"]
                )
                OrderLineItem.objects.bulk_create(processed_order_line_items)

            response_serializer = CreateOrderResponseSerializer({"id": order.id})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        url_path="confirm",
        detail=True,
        permission_classes=[token_permissions.TokenMatchesOASRequirements],
        methods=["post"],
    )
    def confirm_order(self, request: Request, id: UUID = None):
        try:
            order = self.queryset.get(id=id)
            try:
                order.confirm()
                order.save()
            except django_fsm.TransitionNotAllowed:
                if order.state != Order.States.CONFIRMED:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


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
