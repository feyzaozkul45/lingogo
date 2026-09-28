from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render

from lessons import services as lesson_services

from .forms import SignupForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Hoş geldin, {user.username}! Hesabın oluşturuldu.')
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def progress(request):
    stats = lesson_services.get_progress_stats(request.user)
    return render(request, 'accounts/progress.html', {'stats': stats})
