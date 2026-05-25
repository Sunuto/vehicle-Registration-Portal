from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_vehicle, name='register_vehicle'),
    path('my/', views.my_vehicles, name='my_vehicles'),
]