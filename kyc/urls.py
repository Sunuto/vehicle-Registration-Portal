from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_kyc, name='upload_kyc'),
]