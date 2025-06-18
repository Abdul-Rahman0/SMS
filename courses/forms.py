from django import forms
from django.forms import BaseFormSet, formset_factory, inlineformset_factory # Import necessary formset classes
from .models import Submission, Assignment, StudentAssignmentGrade, Session, Attendance, StudentExamGrade, Exam, CourseMaterial # Import Session, Attendance, and Exam models
from users.models import CustomUser # Import CustomUser
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
import logging
from django.contrib.auth import authenticate

# Define common Tailwind CSS classes for form inputs
TAILWIND_INPUT_CLASSES = "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"

class SubmissionForm(forms.ModelForm):
    """
    Form for students to submit assignments.
    """
    class Meta:
        model = Submission
        fields = ['file']

class AssignmentForm(forms.ModelForm):
    """
    Form for teachers to create or update assignments.
    """
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        } 

class GradeAssignmentForm(forms.ModelForm):
    """
    Form for teachers to grade student assignments.
    """
    class Meta:
        model = StudentAssignmentGrade
        fields = ['grade']
        widgets = {
            'grade': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter grade'}),
        } 

class AttendanceForm(forms.ModelForm):
    """
    Form for a single attendance record.
    """
    # You might want to display student name in the form, but the formset handles the student instance.
    class Meta:
        model = Attendance
        fields = ['status']

# Create a formset factory for marking attendance for all students in a session.
# We use BaseFormSet because Attendance records might not exist yet, so we are not editing existing instances initially.
# If you want to edit existing attendance records, consider using modelformset_factory.
# Let's use modelformset_factory as it handles initial data and saving existing instances.
AttendanceFormSet = inlineformset_factory(Session, Attendance, fields=['student', 'status'], extra=0, can_delete=False, form=AttendanceForm, )
# Note: inlineformset_factory is typically used for related objects from a single parent (Session). We need students enrolled in the course, not directly related to the session via a ForeignKey on the Session model itself. A regular modelformset_factory or custom formset might be better.

# Let's redefine using modelformset_factory which is more flexible for a set of model instances (students).
# We will create forms for each student and link them to the session in the view.

class BaseAttendanceFormSet(BaseFormSet):
    """
    Base formset for marking attendance.
    """
    def clean(self):
        if any(self.errors):
            return
        # Add any custom validation for the formset here

# Define the formset dynamically in the view or use a formset factory that takes initial data.
# A simpler approach for marking attendance for a list of students is to pass the students to the template
# and create forms for each student in the template, or use a custom formset in the view.

# Let's stick with a simple ModelForm for now and handle multiple students in the view/template or a custom formset.
# A custom formset is better for handling multiple students on one page.

# Let's create a custom formset in the view that uses AttendanceForm for each student.

# Alternatively, if we assume Attendance records are created automatically for all enrolled students when a session is created,
# then inlineformset_factory could work to edit these existing records.

# Let's refine the plan: create Session objects, and then create placeholder Attendance objects for all enrolled students for that session with a default status (e.g., Absent).
# Then, use inlineformset_factory to easily edit these Attendance objects.

# For now, let's create a basic view that lists students for a session and prepares forms. 

class GradeExamForm(forms.ModelForm):
    """
    Form for teachers to grade student exams.
    """
    class Meta:
        model = StudentExamGrade
        fields = ['grade']
        widgets = {
            'grade': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter grade'}),
        }

class ExamForm(forms.ModelForm):
    """
    Form for teachers to create or update exams.
    """
    class Meta:
        model = Exam
        fields = ['title', 'description', 'exam_date']
        widgets = {
            'exam_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        } 

# New form for uploading course materials
class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': f"{TAILWIND_INPUT_CLASSES} h-24"}), # Add height class
        } 