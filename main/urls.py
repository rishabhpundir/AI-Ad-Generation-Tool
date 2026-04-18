from django.urls import path
from main.views import *

urlpatterns = [
    path("", home, name="home"),
]
