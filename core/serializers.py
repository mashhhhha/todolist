from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import User
from todolist.fields import PasswordField


class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True, write_only=False)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Passwords must match')
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')