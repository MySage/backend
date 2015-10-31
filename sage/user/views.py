from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from models import *
import json


def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


def all_users(request):
    array = list()
    users = User.objects.all()
    for u in users:
        array.append(u)
    return JsonResponse({"users": array})
