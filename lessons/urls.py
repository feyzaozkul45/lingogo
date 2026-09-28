from django.urls import path

from . import views

app_name = 'lessons'

urlpatterns = [
    path('topics/', views.topic_list, name='topic_list'),
    path('lessons/<slug:slug>/', views.lesson_detail, name='lesson_detail'),
]
