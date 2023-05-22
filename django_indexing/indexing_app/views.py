import random
from django.shortcuts import render
from .models import Person, Book
from .serializers import PersonSerializer, BookSerializer, BookSerializerGet, BookSerializerEdit
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .functions import get_city, make_name, get_book_name
from rest_framework.response import Response
# Create your views here.


@api_view(['GET'])
def fetch_person(request):
    try:
        name = request.query_params.get('name')
        queryset = Person.objects.filter(name=name)
        for obj in queryset.iterator(chunk_size=2):
            print(obj.name)
            print(obj.city)
        serializer = PersonSerializer(queryset, many=True)
        # for obj in serializer.data.iterator():
        #     print(obj.name)
        return Response(serializer.data)
    except Exception as error:
        print(error)


@api_view(['POST'])
def add_person(request):
    try:
        for obj in range(15000):
            name = make_name()
            city = get_city()
            person = {"name": name, "city": city}
            serializer = PersonSerializer(data=person)
            if serializer.is_valid():
                serializer.save()
        return Response('data added')
    except Exception as error:
        print(error)


@api_view(['POST'])
def add_book(request):
    try:
        for obj in range(10000):
            print(obj)
            name = get_book_name()
            person = random.choice(range(50000))
            book = {"name": name, "person": person}
            serializer = BookSerializer(data=book)
            if serializer.is_valid():
                serializer.save()
        return Response('Book added.')
    except Exception as error:
        print(error)

@api_view(['GET'])
def get_book(request):
    try:
        queryset = Book.objects.select_related('person').all()
        serializer = BookSerializerGet(queryset, many=True)
        return Response(serializer.data)
    except Exception as error:
        print(error)


@api_view(['PATCH'])
def update_data(request):
    try:
        ids = [2406, 2401, 2402, 2403, 2404, 2405]
        update_list = []
        books = Book.objects.filter(id__in=ids)
        for book in books:
            data = {"name": 'Hello testing', 'person': 100}
            serailizer = BookSerializerEdit(data=data, partial=True)
            if serailizer.is_valid():
                serailizer.update(instance=book, validated_data=data)
                update_list.append(book)
        Book.objects.bulk_update(update_list, ['name'])
        return Response({'msg': f'updated rows ids are {ids}'})

    except Exception as error:
        print(error)
