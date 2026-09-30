from django.urls import path

from . import views

app_name = 'lessons'

urlpatterns = [
    path('topics/', views.topic_list, name='topic_list'),
    path('lessons/<slug:slug>/', views.lesson_detail, name='lesson_detail'),
    path('scenarios/', views.scenario_list, name='scenario_list'),
    path('lessons/<slug:slug>/scenario/', views.scenario_view, name='scenario'),
    path('reading/', views.reading_list, name='reading_list'),
    path('reading/result/<int:attempt_id>/', views.reading_result, name='reading_result'),
    path('reading/<slug:slug>/', views.reading_detail, name='reading_detail'),
]
