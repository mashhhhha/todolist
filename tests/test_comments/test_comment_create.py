from unittest.mock import ANY

import pytest
from django.urls import reverse
from rest_framework import status

from todolist.goals.models import GoalComment


@pytest.mark.django_db
class TestCommentCreateView:
    url = reverse('goals:create-comment')

    def test_create_unauthorized(self, client) -> None:
        """
        When creating Comment Unauthorized user gets Unauthorized error
        """
        response = client.post(self.url, data={})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_without_goal(self, auth_client):
        """
        При создании комментария авторизованный пользователь не передает параметром цель и получает ошибку
        """
        response = auth_client.post(self.url, data={
            'title': 'Comment',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_success(self, auth_client, goal):
        """
        Авторизованный пользователь успешно создает комментарий
        """
        response = auth_client.post(self.url, data={
            'text': 'Test comment',
            'goal': goal.id
        })
        goal_comment = GoalComment.objects.last()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': goal_comment.id,
            'created': ANY,
            'updated': ANY,
            'text': 'Test comment',
            'goal': goal_comment.goal.id
        }
