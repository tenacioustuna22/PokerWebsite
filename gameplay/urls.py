from django.urls import path
from .views import GameplayView



urlpatterns = [
    path("", GameplayView.as_view(), name="gameplay"),
]