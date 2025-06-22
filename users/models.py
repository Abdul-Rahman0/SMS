from django.contrib.auth.models import AbstractUser ,Group
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    # ROLE_CHOICES is now defined at the module level
    
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contactNumber = models.CharField(max_length=20, blank=True, null=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_users',
        verbose_name="Role",
        help_text=('Assign a group to this user'),
    ) # Reference the module-level variable
    dateOfBirth = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    resetToken = models.CharField(max_length=100, null=True, blank=True)
    tokenExpiry = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username