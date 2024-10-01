from uuid import UUID

from django.contrib.auth.hashers import check_password
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from store_api.models import User
from store_api.serializers import (
    CreateUserRequestSerializer,
    UpdateUserPasswordRequestSerializer,
)


class UserViewSet(ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def create(self, request: Request):
        serializer = CreateUserRequestSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create_user(**serializer.validated_data)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
