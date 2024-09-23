from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from store_api.models import User
from store_api.serializers import CreateUserRequestSerializer


class UserViewSet(ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def create(self, request: Request):
        serializer = CreateUserRequestSerializer(data=request.data)
        serializer.is_valid()

        User.objects.create_user(**serializer.validated_data)

        return Response(status=201)
