from django.urls import path
from .views import home_view, contact_view, about_view, student_dashboard_view, user_profile_view

urlpatterns = [
    path('', home_view, name='home'),
    path('contact/', contact_view, name='contact'),
    path('about/', about_view, name='about'),
    path('dashboard/', student_dashboard_view, name='dashboard'),
    path('profile/', user_profile_view, name='profile'),
    
] 