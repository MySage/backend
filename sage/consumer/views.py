from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from models import *
import json
from django.core import serializers
import urllib2, urllib
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def consume(request):
    app_id = "id=762ab8eb-e560-48a9-8b05-a0acd9d5e1fd&subscription-key=9699c87139eb4524977f8cb5078282e2"
    if request.method == "GET":
        return HttpResponseNotAllowed

    message = str(json.loads(request.body)['message'])
    #longitude = float(json.loads(request.body)['longitude'])
    #latitude = float(json.loads(request.body)['latitude'])

    response = json.loads(urllib2.urlopen(str.format("https://api.projectoxford.ai/luis/v1/application?{}&q={}",
                                          app_id, urllib.quote_plus(message))).read())

    intent = response['intents'][0]['intent']

    return JsonResponse(intent)

