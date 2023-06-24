from django.contrib import admin

from todolist.bot.models import TgUser


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id']
    readonly_fields = ['verification_code']
    search_fields = ['chat_id']

    @staticmethod
    def db_user(obj: TgUser) -> str | None:
        if obj.user:
            return obj.user.username
        else:
            return None
