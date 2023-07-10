import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.fields import DateTimeField

from tests.test_goals.factories import CreateGoalRequest
from todolist.goals.models import BoardParticipant, Goal


@pytest.mark.django_db()
class TestCreateGoalView:
    queries_count: int = 5
    url = reverse('goals:create-goal')

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_board_if_not_participant(self, auth_client, goal_category):
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'must be owner or writer in project'}

    def test_failed_to_create_board_if_reader(self, auth_client, board_participant, goal_category):
        board_participant.role = BoardParticipant.Role.reader
        board_participant.save(update_fields=['role'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'must be owner or writer in project'}

    @pytest.mark.parametrize(
        'role', [BoardParticipant.Role.owner, BoardParticipant.Role.writer], ids=['owner', 'writer']
    )
    def test_have_to_create_to_with_roles_owner_or_writer(
            self, auth_client, board_participant, goal_category, role
    ):
        board_participant.role = role
        board_participant.save(update_fields=['role'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        new_goal = Goal.objects.get()
        assert response.json() == _serialize_response(new_goal)

    @pytest.mark.usefixtures('board_participant')
    def test_create_goal_on_not_deleted_category(self, auth_client, goal_category):
        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['not allowed in deleted category']}

    @pytest.mark.usefixtures('board_participant')
    def test_create_goal_on_not_existing_category(self, auth_client):
        data = CreateGoalRequest.build(category=1)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Invalid pk "1" - object does not exist.']}


def _serialize_response(goal: Goal, **kwargs) -> dict:
    data = {
        'id': goal.id,
        'category': goal.category.id,
        'created': DateTimeField().to_representation(goal.created),
        'updated': DateTimeField().to_representation(goal.updated),
        'title': goal.title,
        'description': goal.description,
        'due_date': DateTimeField().to_representation(goal.due_date),
        'status': goal.status,
        'priority': goal.priority
    }

    return data | kwargs
