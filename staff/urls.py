from django.urls import path
from . import views

urlpatterns = [
    path('', views.staff_dashboard, name='staff_dashboard'),
    path('kyc/', views.kyc_review_list, name='kyc_review_list'),
    path('kyc/<int:doc_id>/', views.kyc_review_detail, name='kyc_review_detail'),
    path('users/', views.users_list, name='staff_users_list'),
    path('vehicles/', views.vehicles_list, name='staff_vehicles_list'),
]