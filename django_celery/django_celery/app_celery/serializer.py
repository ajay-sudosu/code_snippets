from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework import serializers


class AuthorSerializer(ModelSerializer):
    full_name = serializers.SerializerMethodField()
    id_author = serializers.SerializerMethodField('author_id')

    class Meta:
        model = Author
        exclude = ('last_name', )

    def get_full_name(self, obj):
        context = self.context
        return obj.first_name + ' ' + obj.last_name

    def author_id(self, obj):
        id = self.context.get("id")
        return id


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class AuthorAddSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class AuthorAddressSerializer(ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Address
        fields = '__all__'


class BookAddSerializer(ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Book
        fields = '__all__'


class AuthorBookSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'
