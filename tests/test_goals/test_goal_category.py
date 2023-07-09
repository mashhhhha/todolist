import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.fields import DateTimeField

from tests.test_goals.factories import CreateGoalCategoryRequest
from todolist.goals.models import BoardParticipant, GoalCategory


@pytest.mark.django_db()
class TestCreateGoalCategoryView:
    queries_count: int = 5
    url = reverse('goals:create-category')

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_category_by_writer(self, client, board, another_user):
        BoardParticipant.objects.create(board=board, user=another_user, role=BoardParticipant.Role.writer)
        client.force_login(another_user)
        data = CreateGoalCategoryRequest(board=board.id)

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        new_category = GoalCategory.objects.get()
        assert response.json() == _serialize_response(new_category)

    def test_failed_to_create_category_by_not_board_participant(self, client, board, another_user):
        client.force_login(another_user)
        data = CreateGoalCategoryRequest(board=board.id)

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_category_by_reader(self, client, board, another_user):
        BoardParticipant.objects.create(board=board, user=another_user, role=BoardParticipant.Role.reader)
        client.force_login(another_user)
        data = CreateGoalCategoryRequest(board=board.id)

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_successful_to_create_category_by_owner(self, board, another_user, client):
        BoardParticipant.objects.create(board=board, user=another_user, role=BoardParticipant.Role.owner)
        client.force_login(another_user)
        data = CreateGoalCategoryRequest(board=board.id)

        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        new_category = GoalCategory.objects.get()
        assert response.json() == _serialize_response(new_category)


def _serialize_response(goal_category: GoalCategory, **kwargs) -> dict:
    data = {
        'id': goal_category.id,
        'created': DateTimeField().to_representation(goal_category.created),
        'updated': DateTimeField().to_representation(goal_category.updated),
        'title': goal_category.title,
        'is_deleted': goal_category.is_deleted,
        'board': goal_category.board.id
    }

    return data | kwargs
