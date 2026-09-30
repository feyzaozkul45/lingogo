from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailOrUsernameAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path('accounts/signup/', views.signup, name='signup'),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=EmailOrUsernameAuthenticationForm,
        ),
        name='login',
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='logout',
    ),
    path('progress/', views.progress, name='progress'),
]
