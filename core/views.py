from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Import messages framework
from .forms import ContactForm, StudentProfileEditForm # Import the ContactForm and StudentProfileEditForm
from users.models import CustomUser, ROLE_CHOICES # Import CustomUser and ROLE_CHOICES
from .models import Course, Assignment, Exam, Payment
from django.db.models import Count, Q # Import Count and Q for aggregations and queries
from django.utils import timezone

def home_view(request):
    """ Render the homepage. """
    return render(request, 'home.html')

def contact_view(request):
    """ Handle contact form submission and render contact page. """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            # Redirect to the same page, or a different success page
            return redirect('contact') # Redirect to the contact URL name
    else:
        form = ContactForm()
        
    # Pass the form to the template context
    return render(request, 'contact.html', {'form': form})

def about_view(request):
    """ Render the about page. """
    return render(request, 'about.html')

@login_required
def user_profile_view(request):
    """
    Display the logged-in user's profile.
    Accessible to any authenticated user (Student, Teacher, Admin).
    """
    # The logged-in user is available as request.user
    user = request.user

    # Specific details like department or specialization might require fetching related objects
    # or adding fields to the CustomUser model if they aren't there.
    # For now, we display fields directly available on CustomUser.

    return render(request, 'profile.html', {'user': user})

@login_required
def user_profile_edit_view(request):
    """
    Allow the logged-in user to edit their profile information.
    Accessible to any authenticated user (Student, Teacher, Admin).
    """
    user = request.user # The logged-in user

    # Use the StudentProfileEditForm for now, as it includes common fields.
    # We might create separate forms or customize this one based on role later if needed.
    if request.method == 'POST':
        form = StudentProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile') # Redirect to the generic profile detail page
    else:
        form = StudentProfileEditForm(instance=user) # Pre-populate the form with existing data

    context = {
        'user': user,
        'form': form,
    }

    return render(request, 'edit_profile.html', context)

@login_required
def student_dashboard_view(request):
    """
    Display the student dashboard.
    Only accessible to authenticated users who are students.
    """
    # Ensure the logged-in user is a student
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    student = request.user # The logged-in user is the student

    # You can add logic here to fetch data for the dashboard, e.g., upcoming assignments, course list summary, etc.
    # For now, we'll just pass the student object.

    return render(request, 'dashboard.html', {'student': student}) 

@login_required
def teacher_dashboard_view(request):
    """
    Display the teacher dashboard.
    Only accessible to authenticated users who are teachers.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get courses assigned to the teacher
    assigned_courses = teacher.courses.all()

    # Get assignments for these courses
    teacher_assignments = Assignment.objects.filter(course__in=assigned_courses).order_by('due_date')

    # Count of pending assignments to grade (assignments with submissions that don't have a grade yet)
    # This requires submissions to be associated with assignments and potentially a 'graded' flag or checking for null grade.
    # Assuming for now that a missing StudentAssignmentGrade means pending grading.
    # A more robust approach might involve a 'is_graded' field on Submission or a separate model.
    pending_grading_count = StudentAssignmentGrade.objects.filter(
        assignment__in=teacher_assignments,
        grade__isnull=True # Assuming null grade means pending grading
    ).count()
     # Note: This counts the number of grades pending, not necessarily the number of submissions if multiple submissions are allowed per student/assignment.
     # If only one submission is allowed (as per the current Submission model unique_together), this count represents assignments needing grading for students who submitted.

    # Get upcoming exams for these courses
    upcoming_exams = Exam.objects.filter(
        course__in=assigned_courses,
        exam_date__gte=timezone.now() # Exams from now onwards
    ).order_by('exam_date')

    context = {
        'teacher': teacher,
        'assigned_courses': assigned_courses,
        'teacher_assignments': teacher_assignments,
        'pending_grading_count': pending_grading_count,
        'upcoming_exams': upcoming_exams,
    }

    return render(request, 'teacher_dashboard.html', context)