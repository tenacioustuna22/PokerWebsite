from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse  

from .models import *

class GameplayView(TemplateView):
    model = Game
    template_name = "gameplay.html"
    success_url = reverse_lazy("gameplay.html")