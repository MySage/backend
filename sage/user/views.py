from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from models import *
from django.core import serializers


def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


def all_users(request):
    users = User.objects.all()
    return JsonResponse(serializers.serialize("json", users), safe=False)
