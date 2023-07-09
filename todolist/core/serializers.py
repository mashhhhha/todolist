from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from todolist.core.models import User
from todolist.fields import PasswordField


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class CreateUserSerializer(serializers.ModelSerializer):
    """This serializer is used during registration process"""

    password = PasswordField(required=True, write_only=False)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict) -> dict:
        """This method serves to validate the passwords"""

        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Passwords must match')
        return attrs


class LoginSerializer(serializers.Serializer):
    """This serializer serves to realize the login process"""

    username = serializers.CharField(required=True)
    password = PasswordField(required=True)


class UpdatePasswordSerializer(serializers.Serializer):
    """The serializer serves to change current user's password"""

    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)
