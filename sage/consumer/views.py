from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from models import *
import json
import oauth2
from django.core import serializers
import urllib2, urllib
from django.views.decorators.csrf import csrf_exempt


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
    #longitude = float(json.loads(request.body)['longitude'])
    #latitude = float(json.loads(request.body)['latitude'])

    response = json.loads(urllib2.urlopen(str.format("https://api.projectoxford.ai/luis/v1/application?{}&q={}",
                                          app_id, urllib.quote_plus(message))).read())

    intent = response.get('intents')[0].get('intent')

    entities = response.get('entities')

    if intent == 'getWeather':
        return HttpResponse(weather(entities=entities, latitude=39, longitude=139))
    if intent == 'getRestaurantInfo':
        return HttpResponse(food(entities=entities, latitude=39, longitude=139))
    return HttpResponse(intent)


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
    api_url = str.format("https://api.yelp.com/v2/search?term={}&ll={},{}&limit=1&sort=1", term, latitude, longitude)
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


