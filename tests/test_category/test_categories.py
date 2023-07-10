from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from tests.factories import BoardFactory, BoardParticipantFactory
from todolist.goals.models import GoalCategory


@pytest.mark.django_db
class TestCategoryCreateView:
    """Тесты для GoalCategory создают представление"""
    url: str = reverse("goals:create-category")

    def test_category_create_owner_moderator(self, auth_client, user) -> None:
        """
        Тест, чтобы проверить, может ли новая категория быть успешно создана,
        когда пользователь является владельцем или модератором доски.
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Owner category",
        }

        response: Response = auth_client.post(self.url, data=create_data)
        created_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Категория не создалась"
        assert created_category, "Созданной категории не существует"
