import logging
import os
from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
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




@login_required
def logout_view(request):
    """ Handle user logout. """
    logout(request)
    return redirect('home') # Redirect to home page after logout


def contact_view(request):
    """ Render the contact page. """
    return render(request, 'contact.html')

def about_view(request):
    """ Render the about page. """
    return render(request, 'about.html') 