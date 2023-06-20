from django.contrib.auth import get_user_model
from django.db import models

USER = get_user_model()


class TgUser(models.Model):
    chat_id = models.BigIntegerField(primary_key=True, editable=False, unique=True)
    user = models.OneToOneField(USER, on_delete=models.CASCADE, null=True, blank=True)
    verification_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'{self.__class__.__name__} {self.chat_id}'
