from django.shortcuts import render


def index(request):
    return render(request, template_name='index.html')


def my_rent(request):
    return render(request, template_name='my-rent.html')
