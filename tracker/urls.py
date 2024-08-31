# tracker/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.compare_excel, name='compare_excel'),
]