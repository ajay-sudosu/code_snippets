from .models import *
from rest_framework.serializers import ModelSerializer


class CreateUserSerializer(ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
