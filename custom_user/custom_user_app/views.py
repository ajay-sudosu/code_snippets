from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import *

# Create your views here.

class CreateUser(APIView):

    def post(self, request):
        try:
            data = request.data
            serializer = CreateUserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors)
            return Response({"msg": "User added"})
        except Exception as e:
            return Response({"msg": str(e)})
