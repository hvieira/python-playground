from uuid import UUID

from django.contrib.auth.hashers import check_password
from oauth2_provider.contrib.rest_framework import permissions as token_permissions
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from store_api.models import User
from store_api.serializers import (
    CreateUserRequestSerializer,
    UpdateUserPasswordRequestSerializer,
    UserPublicProfileSerializer,
)


class UserViewSet(ViewSet):
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
                permission_classes = []

        return [permission() for permission in permission_classes]

    def create(self, request: Request):
        serializer = CreateUserRequestSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create_user(**serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request: Request, pk: UUID = None):
        if request.user.id == pk:
            serializer = UserPublicProfileSerializer(request.user)
        else:
            wanted_user = User.objects.get(pk=pk)
            serializer = UserPublicProfileSerializer(wanted_user)

        return Response(serializer.data)

    # TODO add permission class that the token needs have write scope
    @action(
        url_path="update-password",
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        methods=["post"],
    )
    def update_password(self, request: Request, pk: UUID = None):
        serializer = UpdateUserPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        authenticated_user: User = request.user
        path_user: User = self.queryset.get(pk=pk)

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
