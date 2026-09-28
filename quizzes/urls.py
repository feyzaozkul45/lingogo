from django.urls import path

from . import views

app_name = 'quizzes'

urlpatterns = [
    path('lessons/<slug:slug>/quiz/', views.quiz_view, name='quiz'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='result'),
]
