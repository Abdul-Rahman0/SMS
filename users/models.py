from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

# Define user roles at the module level
ROLE_CHOICES = (
    # ('admin', 'Admin'), # Removed admin role option
    ('teacher', 'Teacher'),
    ('student', 'Student'),
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin') # Use lowercase 'admin' for consistency
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # ROLE_CHOICES is now defined at the module level
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contactNumber = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES) # Reference the module-level variable
    dateOfBirth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    resetToken = models.CharField(max_length=100, null=True, blank=True)
    tokenExpiry = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student' 