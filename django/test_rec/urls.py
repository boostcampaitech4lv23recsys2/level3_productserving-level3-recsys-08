from django.urls import path, include
from .combine import main

app_name = 'test_rec'
urlpatterns = [
    path('fastapi/', include('fastapi.urls'), name='fastapi'),
]