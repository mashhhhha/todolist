# from typing import Callable, Any
#
# from django.core.management import BaseCommand
# from pydantic import BaseModel
#
# from todolist.bot.models import TgUser
# from todolist.bot.tg.client import TgClient
# from todolist.bot.tg.schema import Message
# from todolist.goals.models import Goal, GoalCategory
#
#
# class FSMData(BaseModel):
#     next_handler: Callable
#     data: dict[str, Any] = {}
#
#
# class Command(BaseCommand):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.tg_client = TgClient()
#         self.clients: dict[int, FSMData] = {}
#
#     def handle(self, *args, **options):
#         offset = 0
#
#         self.stdout.write(self.style.SUCCESS('Bot started'))
#         while True:
#             res = self.tg_client.get_updates(offset=offset)
#             for item in res.result:
#                 offset = item.update_id + 1
#                 self.handle_message(item.message)
#
#     def handle_message(self, msg: Message):
#         tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)
#
#         if tg_user.is_verified:
#             self.handle_authorized_user(tg_user, msg)
#         else:
#             tg_user.update_verification_code()
#             self.tg_client.send_message(tg_user.chat_id, f'Your verification code: {tg_user.verification_code}')
#
#     def handle_authorized_user(self, tg_user: TgUser, msg: Message):
#         if msg.text.startswith('/'):
#             if msg.text == '/goals':
#                 self.handle_goals_command(tg_user, msg)
#             elif msg.text == '/create':
#                 self.handle_create_command(tg_user, msg)
#             elif msg.text == '/cancel':
#                 self.clients.pop(tg_user.chat_id, None)
#             else:
#                 self.tg_client.send_message(tg_user.chat_id, 'Command not found')
#         elif tg_user.chat_id in self.clients:
#             client = self.clients[tg_user.chat_id]
#             client.next_handler(tg_user=tg_user, msg=msg, **client.data)
#
#     def handle_goals_command(self, tg_user: TgUser, msg: Message):
#         goals = Goal.objects.exclude(status=Goal.Status.archived).filter(user=tg_user.user)
#         if goals:
#             text = 'Your goals:\n' + '\n'.join([f'{goal.id}) {goal.title}' for goal in goals])
#         else:
#             text = 'You have not goals'
#
#         self.tg_client.send_message(tg_user.chat_id, text)
#
#     def handle_create_command(self, tg_user: TgUser, msg: Message):
#         categories = GoalCategory.objects.filter(user=tg_user.user).exclude(is_deleted=True)
#         if not categories:
#             self.tg_client.send_message(tg_user.chat_id, 'You have not categories')
#             return
#
#         text = 'Select cat to create goal:\n' + '\n'.join([f'{cat.id}) {cat.title}' for cat in categories])
#         self.tg_client.send_message(tg_user.chat_id, text)
#         self.clients[tg_user.chat_id] = FSMData(next_handler=self._get_category)
#
#     def _get_category(self, tg_user: TgUser, msg: Message, **kwargs):
#         try:
#             category = GoalCategory.objects.get(pk=msg.text)
#         except GoalCategory.DoesNotExist:
#             self.tg_client.send_message(tg_user.chat_id, 'Category not exists')
#             return
#         else:
#             self.clients[tg_user.chat_id].next_handler = self._create_goal
#             self.clients[tg_user.chat_id].data['category'] = category
#             self.tg_client.send_message(tg_user.chat_id, 'Set goal title')
#
#     def _create_goal(self, tg_user: TgUser, msg: Message, **kwargs):
#         category = kwargs['category']
#         Goal.objects.create(category=category, user=tg_user.user, title=msg.text)
#         self.tg_client.send_message(tg_user.chat_id, 'New goal created')
#         self.clients.pop(tg_user.chat_id, None)
from django.core.management.base import BaseCommand

from todolist.bot.models import TgUser
from todolist.bot.tg.client import TgClient
from todolist.bot.tg.schema import Message
from todolist.goals.models import Goal, GoalCategory


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self._wait_list = {}

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, msg: Message):
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.user:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        commands: list = ['/goals', '/create', '/cancel']
        create_chat: dict | None = self._wait_list.get(msg.chat.id, None)

        if msg.text == '/cancel':
            self._wait_list.pop(msg.chat.id, None)
            create_chat = None
            self.tg_client.send_message(chat_id=msg.chat.id, text='Operation was canceled')

        if msg.text in commands and not create_chat:
            if msg.text == '/goals':
                qs = Goal.objects.filter(
                    category__is_deleted=False, category__board__participants__user_id=tg_user.user.id
                ).exclude(status=Goal.Status.archived)
                goals = [f'{goal.id} - {goal.title}' for goal in qs]
                self.tg_client.send_message(chat_id=msg.chat.id, text='No goals' if not goals else '\n'.join(goals))

            if msg.text == '/create':
                categories_qs = GoalCategory.objects.filter(
                    board__participants__user_id=tg_user.user.id, is_deleted=False
                )

                categories = []
                categories_id = []
                for category in categories_qs:
                    categories.append(f'{category.id} - {category.title}')
                    categories_id.append(str(category.id))

                self.tg_client.send_message(
                    chat_id=msg.chat.id, text=f'Choose number of category:\n' + '\n'.join(categories)
                )
                self._wait_list[msg.chat.id] = {
                    'categories': categories,
                    'categories_id': categories_id,
                    'category_id': '',
                    'goal_title': '',
                    'stage': 1,
                }
        if msg.text not in commands and create_chat:
            if create_chat['stage'] == 2:
                Goal.objects.create(
                    user_id=tg_user.user.id,
                    category_id=int(self._wait_list[msg.chat.id]['category_id']),
                    title=msg.text,
                )
                self.tg_client.send_message(chat_id=msg.chat.id, text='Goal save')
                self._wait_list.pop(msg.chat.id, None)

            elif create_chat['stage'] == 1:
                if msg.text in create_chat.get('categories_id', []):
                    self.tg_client.send_message(chat_id=msg.chat.id, text='Enter title for goal')
                    self._wait_list[msg.chat.id] = {'category_id': msg.text, 'stage': 2}
                else:
                    self.tg_client.send_message(
                        chat_id=msg.chat.id,
                        text='Enter correct number of category\n' + '\n'.join(create_chat.get('categories', [])),
                    )

        if msg.text not in commands and not create_chat:
            self.tg_client.send_message(chat_id=msg.chat.id, text=f'Unknown command!')

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        code = tg_user._generate_verification_code()
        tg_user.verification_code = code
        tg_user.save()

        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Hello! Verification code: {code}')
