from typing import Any

import requests
from pydantic import ValidationError

from todolist import settings
from todolist.bot.tg.schema import GetUpdatesResponse, SendMessageResponse


class TgClient:
    """TgClient class contains methods to manage telegram bot"""

    def __init__(self, token: str | None = None) -> None:
        """Initialize the TgClient class
        :param token: A string representing the telegram bot token
        """
        self.__token = token if token else settings.BOT_TOKEN
        self.__base_url = f'https://api.telegram.org/bot{self.__token}/'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        """This method serves to send update request to telegram API,
        get response and return GetUpdatesResponse instance
        :param offset: An integer representing the offset to get certain
        update message
        :param timeout: An integer representing the seconds to wait for
        response
        :return: A GetUpdatesResponse instance
        """
        data = self._get('getUpdates', offset=offset, timeout=timeout)
        return GetUpdatesResponse(**data)

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        """This method serves to send a message to telegram API
        :param chat_id: An integer representing the telegram chat id
        :param text: A string representing the message to send
        :return: A SendMessageResponse instance containing a result of the
        operation
        """
        data = self._get('sendMessage', chat_id=chat_id, text=text)
        return SendMessageResponse(**data)

    def __get_url(self, method: str) -> str:
        """This method returns the configured telegram url
        :param method: A string representing a method to add in telegram url
        :return: A string representing the telegram url with token and
        requested method
        """
        return f'{self.__base_url}{method}'

    def _get(self, command: str, **params: Any) -> dict:
        """This method prepare response for methods sendMessage and getUpdates
        :param method: A string of method
        :param **params: A dictionary with parameters
        return: json file for methods
        """
        url = self.__get_url(command)
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
