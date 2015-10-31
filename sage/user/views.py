from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from models import *
import json
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def index(request):
    return HttpResponse("Hello, world. You're at the user index.")


def all_users(request):
    users = User.objects.values('name', 'password', 'phone_number')
    return JsonResponse(dict(users=list(users)))


@csrf_exempt
def login(request):
    return HttpResponse(request.body)
