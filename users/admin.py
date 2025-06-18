from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'name', 'role', 'is_staff', 'is_active'] # Fields displayed in the list view
    list_filter = ['role', 'is_staff', 'is_active'] # Filters in the right sidebar
    search_fields = ['email', 'name'] # Fields searchable
    ordering = ['email'] # Default ordering
    # Define fieldsets for adding and changing users
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'role', 'contactNumber', 'dateOfBirth', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'createdAt')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'name', 'role', 'contactNumber', 'dateOfBirth', 'gender'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin) 