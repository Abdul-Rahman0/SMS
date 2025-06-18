import logging
import os
from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, ManualAuthenticationForm
from .models import CustomUser # Assuming CustomUser is in models.py
from django.contrib import messages # Import messages
from django.views.decorators.csrf import csrf_exempt # Import csrf_exempt

logger = logging.getLogger(__name__)

def home_view(request):
    """ Render the homepage with dynamic background images from media folder. """
    media_dir = settings.MEDIA_ROOT
    image_files = [
        f for f in os.listdir(media_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    ]
    print("Image files found:", image_files)
    image_urls = [settings.MEDIA_URL + f for f in image_files]
    print("Image URLs:", image_urls)
    return render(request, 'home.html', {'background_images': image_urls})

def register_view(request):
    """ Handle user registration. """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Redirect to home page after successful registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """ Handle user login. """
    logger.info("Attempting login...")
    if request.method == 'POST':
        form = ManualAuthenticationForm(request, request.POST)
        try:
            if form.is_valid():
                user = form.user
                if user.is_active:
                    login(request, user)
                    logger.info(f"User {user.email} logged in successfully. Redirecting to home.")
                    return redirect('home')  # Redirect to home page after successful login
                else:
                    logger.warning(f"Authentication successful for inactive user: {user.email}")
                    messages.error(request, 'Your account is inactive.')
            else:
                logger.info(f"ManualAuthenticationForm is not valid. Errors: {form.errors}")
                pass

        except Exception as e:
            logger.error("Exception during form processing or authentication: %s", e, exc_info=True)
            messages.error(request, "An unexpected error occurred during login. Please try again.")

    else:
        form = ManualAuthenticationForm(request=request)

    logger.info("Rendering login page.")
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    """ Handle user logout. """
    logout(request)
    return redirect('home') # Redirect to home page after logout

@login_required
def profile_view(request):
    """ Display and update user profile. """
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile') # Redirect to profile page after successful update
    else:
        form = CustomUserChangeForm(instance=user)
    # Note: For profile editing by the user themselves, you might want a simpler form
    # than CustomUserChangeForm (which includes permissions). We'll refine this later
    # in the template or by creating a separate profile edit form if needed.
    return render(request, 'users/profile.html', {'form': form, 'user': user})

def contact_view(request):
    """ Render the contact page. """
    return render(request, 'contact.html')

def about_view(request):
    """ Render the about page. """
    return render(request, 'about.html') 