from django import forms
from .models import ContactMessage # Import ContactMessage from core.models
from users.models import CustomUser
from django.core.exceptions import ValidationError
from .models import AssignmentSubmit


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'email': forms.EmailInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'message': forms.Textarea(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32'}),
        }



class AssignmentSubmitForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmit
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        assigment = cleaned_data.get('assigment')
        submitted_by = cleaned_data.get('submitted_by')

        if assigment and submitted_by:
            if AssignmentSubmit.objects.filter(assigment=assigment, submitted_by=submitted_by).exists():
                raise ValidationError("You have already submitted this assignment.")

        return cleaned_data

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