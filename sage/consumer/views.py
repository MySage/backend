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
import random

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
            return JsonResponse(dict(message=weather(entities=entities, latitude=42, longitude=-71), type='weather'))
        if intent == 'getRestaurantInfo':
            return JsonResponse(dict(message=food(entities=entities, latitude=42, longitude=-71), type='food'))
        if intent == 'doEquation':
            return JsonResponse(dict(message=math(entities=entities), type='math'))
        if intent == 'getGreeting':
            return JsonResponse(dict(message=greetings(entities=entities), type='greeting'))
        if intent == 'getStocks':
            return JsonResponse(dict(message=stocks(entities=entities), type='stocks'))
        if intent == 'getCompliment':
            return JsonResponse(dict(message=compliment(), type='compliment'))
        if intent == 'None':
            return JsonResponse(dict(message="What do you mean?", type='exception'))

    speech = ''
    for r in response.get('positive'):
        return JsonResponse(dict(message=compliment(), type='compliment'))
    for r in response.get('negative'):
        speech += "Hey! I " + r.get('sentiment') + " " + r.get('topic') + " too!\n"

    return JsonResponse(dict(message=speech if len(speech) > 0 else "What do you mean?"))


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
    api_url = str.format("https://api.yelp.com/v2/search?term={}&ll={},{}&limit=1&radius_filter=15000&sort=0",
                         urllib.quote_plus(term), latitude, longitude)
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

    if equation == '':
        return ''

    api_url = ''
    if math_operation == '':
        api_url = str.format("http://api.wolframalpha.com/v2/query?appid=KYP3UW-J5AA9E5U9W&input={}&format=image", urllib.quote(equation))
    else:
        math_request = math_operation + ' ' + equation
        api_url = str.format("http://api.wolframalpha.com/v2/query?appid=KYP3UW-J5AA9E5U9W&input={}&format=image",
                         urllib.quote_plus(math_request))


    xml_response = urllib2.urlopen(url=api_url).read()
    root = elementTree.fromstring(xml_response)

    for child in root:
        child_attrib = child.attrib
        if child.tag == "pod":
            text = child_attrib["title"]
            if text == "Plots" or text == "Result" or text == "Plot": 
                for subpod in child:
                    for image in subpod:
                        return image.attrib["src"]
    
    return ''


def greetings(entities):
    greetings = ['hey lovely','hey good looking', 'hello', 'hey good looking', 'what up?',
                 'hi there', 'Hi, my name is Sage', 'hey good looking', 'sup homie', 'what up homie?', 'hey poopie head <3', 'Hey, I am Sage, your personal asisstant and BFFL']
    rand_int = random.randint(0, len(greetings) - 1)
    return greetings[rand_int]

def compliment():
    compliments = ['thank you', 'thanks', 'much appreciated', 'you are the best', 'that is awesome', 'cool beans', 'yeye', 'sweet, thanks', 'thanks cutie pie', 'aw shucks', '<3', 'love ya']
    rand_int = random.randint(0, len(compliments) - 1)
    return compliments[rand_int]

def stocks(entities):
    ticker = ''

    for entity in entities:
        if entity.get('type') == "Search":
            ticker = entity.get('entity')

    if ticker == '':
        return None
    api_url = str.format("http://dev.markitondemand.com/Api/v2/Quote/json?symbol={}", ticker)

    response = json.loads(urllib2.urlopen(url=api_url).read())

    name = response.get('Name')
    open = response.get('Open')
    last_price = response.get('LastPrice')

    return name + "\n" + str(open) + "\n" + str(last_price)
