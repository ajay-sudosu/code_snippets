from django.shortcuts import render
from .models import Hello
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .serializer import HelloSerializer
# Create your views here.


def helloView(request):
    try:
        if request.method == 'GET':
            hello = Hello.objects.all()
            context = {"hello": hello, "score": 20}
            return render(request, 'settings_app/home.html', context=context)
    except Exception as error:
        print(e)


class HelloDetailView(DetailView):
    model = Hello
    template_name = 'settings_app/detail.html'


def helloDetail(request, id):
    try:
        if request.method == 'GET':
            hello = get_object_or_404(Hello, id=id)
            context = {"hello": hello, 'id': id}
            return render(request, 'settings_app/detail.html', context=context)
    except Exception as e:
        print(e)
