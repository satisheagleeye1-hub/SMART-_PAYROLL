from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import LoginForm


@csrf_protect
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:admin_dashboard' if request.user.is_admin else 'dashboard:employee_dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.status == 'Active':
                login(request, user)
                messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
                if user.is_admin:
                    return redirect('dashboard:admin_dashboard')
                else:
                    return redirect('dashboard:employee_dashboard')
            else:
                messages.error(request, 'Invalid credentials or account is inactive.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out the current user and redirect to login page. Accepts GET and POST to be resilient to link/form calls."""
    # Call Django logout; it's safe to call even if user is not authenticated
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})
