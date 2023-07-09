import pytest
from django.urls import reverse
from rest_framework import status

from tests.test_core.factories import LoginRequest


@pytest.mark.django_db()
class TestLoginView:
    url = reverse('core:login')

    def test_user_does_not_exists(self, client):
        data = LoginRequest.create()

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_password(self, client, user):
        data = LoginRequest.create(username=user.username)

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN