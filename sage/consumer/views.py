from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from models import *
import json
import oauth2
from django.core import serializers
import urllib2, urllib
from django.views.decorators.csrf import csrf_exempt
import xml.etree.ElementTree as elementTree


CONSUMER_KEY = "a2TXKaRYAalONAuHnIA9yA"
CONSUMER_SECRET = "1sSDt-631lGzN5BmzY0iRLnj7dI"
TOKEN = "KBc_ZybZ53dJ0nkzZZou3KhgLa-ZnceI"
TOKEN_SECRET = "HY3J3MLjOEEA5uh-t2TE-YVaJnI"


@csrf_exempt
def consume(request):
    app_id = "id=762ab8eb-e560-48a9-8b05-a0acd9d5e1fd&subscription-key=9699c87139eb4524977f8cb5078282e2"
    if request.method == 'GET':
        return HttpResponseNotAllowed

    message = str(json.loads(request.body)['message'])
    response = json.loads(urllib2.urlopen(
        str.format("https://api.havenondemand.com/1/api/sync/analyzesentiment/v1?text={}&apikey=5d1ba3b9-3913-4e21-8f1f-fcfd398bfaf3",
                   urllib.quote_plus(message))).read())

    if len(response.get('positive')) < 1 and len(response.get('negative')) < 1 and \
            response.get('aggregate').get('sentiment') == 'neutral':

        #longitude = float(json.loads(request.body)['longitude'])
        #latitude = float(json.loads(request.body)['latitude'])

        response = json.loads(urllib2.urlopen(str.format("https://api.projectoxford.ai/luis/v1/application?{}&q={}",
                                              app_id, urllib.quote_plus(message))).read())

        intent = response.get('intents')[0].get('intent')

        entities = response.get('entities')

        if intent == 'getWeather':
            return JsonResponse(dict(message=weather(entities=entities, latitude=42, longitude=-71)))
        if intent == 'getRestaurantInfo':
            return JsonResponse(dict(message=food(entities=entities, latitude=42, longitude=-71)))
        if intent == 'doEquation':
            return JsonResponse(dict(message=math(entities=entities)))

    speech = ''
    for r in response.get('positive'):
        speech += "Hey! I " + r.get('sentiment') + " " + r.get('topic') + " too!\n"
    for r in response.get('negative'):
        speech += "Hey! I " + r.get('sentiment') + " " + r.get('topic') + " too!\n"

    return JsonResponse(dict(message=speech))


def weather(entities, latitude, longitude):

    api_url = str.format("http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}"
                         "&appid=88ab028ab3f5325465e618dd3a8e4a17", latitude, longitude)

    response = json.loads(urllib2.urlopen(url=api_url).read())

    return response.get('weather')[0].get('description')

    # term = ''
    # for entity in entities:
    #     if entity.get('type') == "Information":
    #         term = entity.get('entity')
    #
    # if term in response.get('weather').get('main') or term in response.get('weather').get('description'):
    #     return response.get('weather').get('description')
    #
    # if term in response:
    #


def food(entities, latitude, longitude):

    term = 'food'
    for entity in entities:
        if entity.get('type') == "Search":
            term = entity.get('entity')

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    api_url = str.format("https://api.yelp.com/v2/search?term={}&ll={},{}&limit=1", urllib.quote_plus(term)
                         , latitude, longitude)
    oauth_request = oauth2.Request(method="GET", url=api_url)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )

    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()

    response = json.loads(urllib2.urlopen(url=signed_url).read())

    return response.get('businesses')[0].get('name') + " " + \
           response.get('businesses')[0].get('location').get('display_address')[0]


def math(entities):
    base_url = 'http://api.wolframalpha.com/v2/query?appid=xxx'
    math_operation = ''
    equation = ''   

    for entity in entities:
        if entity.get('type') == "MathOperation":
            math_operation = entity.get('entity')
        if entity.get('type') == "Equation":
            equation = entity.get('entity')

    if math_operation == '' and equation == '':
        return ''

    math_request = math_operation + ' ' + equation
    api_url = str.format("http://api.wolframalpha.com/v2/query?appid=KYP3UW-35R4EETYA3&input={}&format=image", urllib.quote_plus(math_request))
    xml_response =  urllib2.urlopen(url=api_url).read()
    tree = elementTree.fromstring(xml_response)
    root = tree.getroot()

    return root

    # for pod in root.findall('pod'):
    #     return pod
        # if pod.get('title') == "Plots":
        #     return pod
        #     subpod = pod.find('subpod')
        #     image = subpod.find('img')
        #     return image.get('src')


