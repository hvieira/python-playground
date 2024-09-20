from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from store_api.models import User
from store_api.requests import CreateUserRequest
from store_api.serializers import CreateUserRequestSerializer


class UserViewSet(ViewSet):

    queryset = User.objects.all()

    def create(self, request: Request):
        serializer = CreateUserRequestSerializer(data=request.data)
        serializer.is_valid()

        # TODO there's no need for this request class it seems
        # request = CreateUserRequest(**serializer.validated_data)


        create_user = User.objects.create_user(**serializer.validated_data)

        return Response(status=201)
