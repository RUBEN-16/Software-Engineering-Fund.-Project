from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.page, name='Page'),
    path('login/', views.log, name = 'Login'),
    path('register/', views.registration, name = 'Register'),
]

