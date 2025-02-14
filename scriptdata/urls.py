from django.urls import path
from scriptdata.views import generate_ad


urlpatterns = [
    path("generate-ad/", generate_ad, name="generate_ad"),
]
