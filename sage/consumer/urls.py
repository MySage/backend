from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'send_message/', views.consume, name='message'),
]