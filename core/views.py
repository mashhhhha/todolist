from typing import Any

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.serializers import CreateUserSerializer, ProfileSerializer
from rest_framework.serializers import Serializer


class SignUpView(GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(**serializer.data)

        return Response(ProfileSerializer(user).data, status=status.HTTP_201_CREATED)

