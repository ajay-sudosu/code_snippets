from rest_framework.serializers import ModelSerializer
from .models import Person, Book

class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

    def create(self, validated_data):
        return Person.objects.create(**validated_data)


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        return Book.objects.create(**validated_data)


class BookSerializerGet(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookSerializerEdit(ModelSerializer):
    person = PersonSerializer(read_only=True)
    class Meta:
        model = Book
        fields = '__all__'

    def update(self, instance, validated_data):
        person = validated_data.pop('person')
        instance.name = validated_data.get('name', instance.name)
        instance.person = person
        instance.save()
        return super().update(instance, validated_data)
        # return instance

    # def update(self, instance, validated_data):
    #
    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)
    #     instance.save()
    #     return instance


