from django.shortcuts import render
from django.views.generic import View
from django.http.response import HttpResponse
from . models import Products
from django.http import JsonResponse
import requests


def index(request):
    products = Products.objects.all()
    context = {"products": products}
    return render(request, 'index.html', context)


def products(request, id):
    product = Products.objects.get(id=id)
    if "recently_viewed" in request.session:
        if id in request.session['recently_viewed']:
            request.session['recently_viewed'].pop()
            request.session['recently_viewed'].insert(0, id)
        else:
            request.session['recently_viewed'].insert(0, id)
        if len(request.session['recently_viewed']) > 5:
            request.session['recently_viewed'].pop()
        else:
            pass
    else:
        request.session['recently_viewed'] = [id]
    recently_viewed = Products.objects.filter(id__in=request.session['recently_viewed']).order_by('-updated_at')
    request.session.modified = True
    context = {"product": product, "viewed": recently_viewed}
    return render(request, 'products.html', context)


def load_data(request,):
    res = requests.get('https://fakestoreapi.com/products')
    for data in res.json():
        result = {"title": data['title'],
                  "price": data['price'],
                  "description": data['description'],
                  "image_url": data['image']}
        products = Products(**result)
        products.save()

    return render(request, 'load_data.html')
