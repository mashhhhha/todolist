import factory.django


class LoginRequest(factory.DictFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')