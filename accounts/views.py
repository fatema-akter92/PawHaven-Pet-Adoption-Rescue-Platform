from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.authtoken.models import Token
from .forms import CustomRegisterForm, CustomLoginForm
from pets.models import AdoptionRequest, Favorite


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create API token automatically for the user
            Token.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to PawHaven, {user.first_name or user.username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = CustomRegisterForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Ensure API token exists
            Token.objects.get_or_create(user=user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    token, _ = Token.objects.get_or_create(user=user)
    
    # User adoption stats
    applications = AdoptionRequest.objects.filter(user=user)
    total_apps = applications.count()
    pending_apps = applications.filter(status='Pending').count()
    approved_apps = applications.filter(status='Approved').count()
    rejected_apps = applications.filter(status='Rejected').count()
    
    # Favorites count
    favorites_count = Favorite.objects.filter(user=user).count()

    context = {
        'token': token.key,
        'total_apps': total_apps,
        'pending_apps': pending_apps,
        'approved_apps': approved_apps,
        'rejected_apps': rejected_apps,
        'favorites_count': favorites_count,
        'recent_applications': applications[:3],
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def regenerate_token_view(request):
    if request.method == 'POST':
        Token.objects.filter(user=request.user).delete()
        new_token = Token.objects.create(user=request.user)
        messages.success(request, "Your API token has been regenerated successfully!")
    return redirect('profile')
