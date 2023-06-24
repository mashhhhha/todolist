from typing import Any

import requests
from pydantic import ValidationError

from todolist import settings
from todolist.bot.tg.schema import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token: str | None = None) -> None:
        self._token = token if token else settings.BOT_TOKEN
        self._base_url = f'https://api.telegram.org/bot{self._token}/'
        print()

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        data = self._get('getUpdates', offset=offset, timeout=timeout)
        try:
            return GetUpdatesResponse(**data)
        except ValidationError:
            return GetUpdatesResponse(ok=False, result=[])

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        data = self._get('sendMessage', chat_id=chat_id, text=text)
        return SendMessageResponse(**data)

    def __get_url(self, method: str) -> str:
        return f'{self._base_url}{method}'

    def _get(self, command: str, **params: Any) -> dict:
        url = self.__get_url(command)
        params['timeout'] = 10
        response = requests.get(url, params=params)
        if not response.ok:
            print(f'Invalid status code from telegram {response.status_code} on command {command}')
            return {'ok': False, 'result': []}
        return response.json()


def _serialize_response(serializer_class, data):
    try:
        return serializer_class(**data)
    except ValidationError as e:
        print(f'Failed to serializer telegram response due {e}')
        raise ValueError
