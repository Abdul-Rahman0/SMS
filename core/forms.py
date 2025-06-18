from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import ContactMessage # Import ContactMessage from core.models
from users.models import CustomUser, ROLE_CHOICES # Import CustomUser and ROLE_CHOICES from users.models

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for creating new users.
    Inherits from UserCreationForm but uses the custom User model.
    """
    # Ensure that required fields from your custom User model are included
    # The UserCreationForm by default includes email (if USERNAME_FIELD='email') and password
    # We need to explicitly add 'name' and 'role'
    name = forms.CharField(max_length=255, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    contactNumber = forms.IntegerField(required=True)
    dateOfBirth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    gender = forms.CharField(max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        # Use your custom User model
        model = CustomUser
        # Specify the fields to include in the form
        # USERNAME_FIELD ('email') and password fields are handled by UserCreationForm's Meta
        # We add the extra fields required by your model
        fields = ('email', 'name', 'role', 'contactNumber', 'dateOfBirth', 'gender')
        # You might want to add the password fields explicitly if needed,
        # but UserCreationForm handles them well by default.

    def save(self, commit=True):
        # Override save to handle the custom fields
        user = super().save(commit=False)
        # Assign values from the form fields to the user object
        user.name = self.cleaned_data['name']
        user.role = self.cleaned_data['role']
        user.contactNumber = self.cleaned_data['contactNumber']
        user.dateOfBirth = self.cleaned_data['dateOfBirth']
        user.gender = self.cleaned_data['gender']
        # Handle other fields if necessary

        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """
    A custom form for updating existing users.
    Inherits from UserChangeForm but uses the custom User model.
    """
    class Meta:
        model = CustomUser
        # For the change form, you typically list all editable fields
        fields = ('email', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions') # Example fields
        # You might inherit from UserChangeForm.Meta and adjust fields if needed,
        # but explicitly listing is safer if you're unsure of parent fields.

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'email': forms.EmailInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'message': forms.Textarea(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32'}),
        }

class StudentProfileEditForm(forms.ModelForm):
    """
    Form for students to edit their profile information.
    """
    class Meta:
        model = CustomUser
        fields = ['name', 'contactNumber', 'dateOfBirth', 'gender']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'contactNumber': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'dateOfBirth': forms.DateInput(attrs={'type': 'date', 'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'gender': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            # Add other fields here if you make them editable by the user
        } 