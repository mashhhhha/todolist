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
        self.stdout.write(self.style.SUCCESS('Bot started'))
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
