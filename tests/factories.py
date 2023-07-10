import factory.django
from django.contrib.auth import get_user_model
from django.utils import timezone
from pytest_factoryboy import register

from todolist.bot.models import TgUser
from todolist.core.models import User
from todolist.goals.models import Board, BoardParticipant, GoalCategory, Goal, GoalComment

USER_MODEL = get_user_model()


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        return User.objects.create_user(*args, **kwargs)


class SignUpRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    password_repeat = factory.LazyAttribute(lambda o: o.password)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)

    class Meta:
        abstract = True


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class GoalCategoryFactory(DatesFactoryMixin):
    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory


@register
class GoalFactory(DatesFactoryMixin):
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    title = factory.Faker('catch_phrase')

    class Meta:
        model = Goal


@register
class GoalCommentFactory(DatesFactoryMixin):
    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)
    text = factory.Faker('sentence')

    class Meta:
        model = GoalComment


@register
class TgUserFactory(factory.django.DjangoModelFactory):
    telegram_chat_id = factory.Faker('random_int', min=1)

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        obj = TgUser.objects.create(*args, **kwargs)
        obj.update_verification_code()
        return obj

    class Meta:
        model = TgUser


@register
class CategoryFactory(DatesFactoryMixin):
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory
