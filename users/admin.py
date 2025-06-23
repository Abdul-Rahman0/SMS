from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    
    model = CustomUser
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email',
                       'first_name', 'last_name', 'group','gender','contactNumber'),
        }),
    )
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email',
                       'first_name', 'last_name', 'group','gender','contactNumber')
        }),

    )
    list_display = ['email', 'name', 'group', 'is_staff', 'is_active'] # Fields displayed in the list view
    list_filter = ['group', 'is_staff', 'is_active'] # Filters in the right sidebar
    search_fields = ['email', 'name'] # Fields searchable
    ordering = ['email'] # Default ordering
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(is_superuser=True)
    # Define fieldsets for adding and changing users

    def save_model(self, request, obj, form, change):
        # First save the user
        super().save_model(request, obj, form, change)

        # Then handle group assignment
        if obj.group:
            # Clear existing groups
            obj.groups.clear()
            # Add the new group
            obj.groups.add(obj.group)
            # Set is_staff to True if user has a group
            # obj.is_staff = True
            # obj.is_active = True
            obj.save()

admin.site.register(CustomUser, CustomUserAdmin) 