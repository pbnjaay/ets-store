from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def say_hello(request):
    x = 2
    y = 5
    return render(request, 'hello.html', context={'name': 'bassirou'})
