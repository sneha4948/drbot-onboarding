from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('phc/', views.register_phc, name='register_phc'),
    path('vc/', views.register_user, name='register_vc'),
    path('staff/', views.register_staff, name='register_staff'),
    path('delete/', views.delete_user, name='delete_user'),
]
