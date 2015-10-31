from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from models import *
import json
from django.core import serializers
import urllib2
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def consume(request):
    if request.method == "GET":
        return HttpResponseNotAllowed

    json_data = json.loads(request.body)
    response = urllib2.urlopen("https://api.projectoxford.ai/luis/v1/application?id=762ab8eb-e560-48a9-8b05-a0acd9d5e1fd&subscription-key=9699c87139eb4524977f8cb5078282e2&q=rain").read()
    return response

