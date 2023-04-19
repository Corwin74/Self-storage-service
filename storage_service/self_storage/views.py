from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, template_name='index.html')


@login_required(login_url='/')
def my_rent(request):
    context = {}
    return render(request, template_name='my-rent.html', context=context)

