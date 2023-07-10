from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from todolist.bot.tg.client import TgClient
from todolist.core.models import User


@pytest.mark.django_db()
class TestTgUser:
    url = reverse('bot:bot-verify')

    def test_user_verified(self, auth_client, user: User, tg_user_factory):
        tg_user = tg_user_factory.create(user=None)
        data = {'verification_code': tg_user.verification_code}

        with patch.object(TgClient, 'send_message'):
            response = auth_client.patch(self.url, data=data)

        tg_user.refresh_from_db()
        assert tg_user.user == user
        assert response.status_code == status.HTTP_200_OK

    def test_bot_send_message_in_telegram(self, auth_client, tg_user):
        data = {'verification_code': tg_user.verification_code}

        with patch.object(TgClient, 'send_message') as mock:
            response = auth_client.patch(self.url, data=data)

        assert response.status_code == status.HTTP_200_OK
        mock.assert_called_once_with(tg_user.telegram_chat_id, 'Bot token verified')

    def test_invalid_verification_code(self, tg_user_factory, auth_client):
        tg_user = tg_user_factory.create(verification_code='code')
        data = {'verification_code': 'incorrect'}

        with patch.object(TgClient, 'send_message') as mock:
            response = auth_client.patch(self.url, data=data)

        tg_user.refresh_from_db()
        assert tg_user.user is None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock.assert_not_called()
