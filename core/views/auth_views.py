from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from core.forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'ngo':
                messages.success(request, 'Registration successful! Your NGO account is pending admin approval.')
                return redirect('login')
            else:
                login(request, user)
                messages.success(request, 'Registration successful!')
                if user.role == 'donor': return redirect('donor_dashboard')
                if user.role == 'needy': return redirect('needy_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == 'ngo' and not user.is_approved:
                messages.error(request, 'Your NGO account is pending admin approval.')
                return redirect('login')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            if user.role == 'donor': return redirect('donor_dashboard')
            elif user.role == 'ngo': return redirect('ngo_dashboard')
            elif user.role == 'needy': return redirect('needy_dashboard')
            elif user.role == 'admin' or user.is_superuser: return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
