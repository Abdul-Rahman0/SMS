from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser, ROLE_CHOICES
import logging
from django.contrib.auth import authenticate

# Define common Tailwind CSS classes for form inputs
TAILWIND_INPUT_CLASSES = "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from an email and
    password.
    """
    # Define fields with widgets and added Tailwind classes
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES}))
    name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}))
    contactNumber = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}))
    dateOfBirth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}))
    gender = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}))

    class Meta:
        model = CustomUser
        # Explicitly list fields, including 'email' (the USERNAME_FIELD) and NOT 'username'
        # UserCreationForm will automatically handle password and password2
        fields = ('email', 'name', 'role', 'contactNumber', 'dateOfBirth', 'gender')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        # Ensure password hashing is handled by the base class
        user = super().save(commit=False)

        # Set additional fields on the user instance
        user.role = self.cleaned_data["role"]
        user.name = self.cleaned_data["name"]
        user.contactNumber = self.cleaned_data["contactNumber"]
        user.dateOfBirth = self.cleaned_data["dateOfBirth"]
        user.gender = self.cleaned_data["gender"]

        # Save the user instance with the additional fields
        if commit:
            user.save()

        return user

# Create a new manual authentication form
class ManualAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        logger = logging.getLogger(__name__)
        logger.info(f"ManualAuthenticationForm clean method: Attempting to authenticate {email}")

        if email and password:
            user = authenticate(request=self.request, username=email, password=password)
            if user is None:
                logger.warning(f"Manual authentication failed for email: {email}")
                raise forms.ValidationError(
                    'Please enter a correct email and password.'
                )
            # Store the authenticated user on the form instance
            self.user = user
            logger.info(f"Manual authentication successful for user: {user.email}")
        else:
            logger.warning("Manual authentication clean method: Email or password not provided.")

        return self.cleaned_data

    # Add a request attribute to the form for authenticate function
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASSES})) # Add classes to role field

    class Meta:
        model = CustomUser
        # Include relevant fields for editing and apply classes
        fields = ('email', 'name', 'role', 'contactNumber', 'dateOfBirth', 'gender', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        widgets = {
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'contactNumber': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'dateOfBirth': forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
            'gender': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            # Add other fields from the 'fields' tuple here to apply classes if needed
            # Example for is_active (BooleanCheckox is default, might not need classes or different classes)
            # 'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You might want to exclude certain fields from the profile update form
        # For example, in a user's own profile edit, they shouldn't change permissions
        # This form is also used in the Django Admin, so keep all fields there.
        # We will handle which fields are shown in the profile view template/view logic.
        pass 