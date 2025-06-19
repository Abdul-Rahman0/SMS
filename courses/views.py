print("Loading courses.views...")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, CourseSchedule, Assignment, Exam, StudentAssignmentGrade, StudentExamGrade, Payment, Submission, Session, Attendance, Enrollment, CourseMaterial # Import necessary models from courses.models
from users.models import CustomUser # Import CustomUser from users.models
from core.models import StudentProfile, Course, Enrollment # Import StudentProfile from core.models and Course from core.models
from django.db import IntegrityError
from django.utils import timezone # Import timezone
from .forms import SubmissionForm, AssignmentForm, GradeAssignmentForm, AttendanceForm, GradeExamForm, ExamForm, CourseMaterialForm # Import SubmissionForm, AssignmentForm, and GradeAssignmentForm, GradeExamForm, ExamForm, CourseMaterialForm
from django.forms import modelformset_factory, inlineformset_factory, BaseFormSet, formset_factory # Import modelformset_factory, inlineformset_factory, BaseFormset, formset_factory
import logging
from django import forms

@login_required
def course_list_view(request):
    """
    Display a list of all available courses. Students can enroll in any course.
    """
    user = request.user
    all_courses = Course.objects.all()
    enrolled_course_ids = []
    if user.is_authenticated and hasattr(user, 'role') and user.role == 'student':
        enrolled_courses = user.core_enrollments.values_list('course__course_id', flat=True)
        enrolled_course_ids = list(enrolled_courses)

        # Handle enroll/drop POST
        if request.method == 'POST':
            course_id = int(request.POST.get('course_id'))
            if 'enroll' in request.POST and course_id not in enrolled_course_ids:
                Enrollment.objects.create(student=user, course_id=course_id)
                # Create a pending payment for this course if not already exists
                course = Course.objects.get(course_id=course_id)
                Payment.objects.get_or_create(
                    student=user,
                    description=f"Course Fee: {course.course_name}",
                    amount=1000,
                    status='pending',
                    defaults={
                        'payment_date': timezone.now(),
                    }
                )
            elif 'drop' in request.POST and course_id in enrolled_course_ids:
                Enrollment.objects.filter(student=user, course_id=course_id).delete()
                # Optionally, you could also delete the payment or mark as cancelled
            return redirect('courses:course_list')

    context = {
        'all_courses': all_courses,
        'enrolled_course_ids': enrolled_course_ids,
    }
    return render(request, 'courses/course_list.html', context)

@login_required
def enroll_course_view(request, course_id):
    """
    Allow a student to enroll in a course.
    """
    # Ensure the logged-in user is a student and get their department
    user = request.user
    if not hasattr(user, 'role') or user.role != 'student':
        messages.error(request, 'You do not have permission to enroll in courses.')
        return redirect('course_list') # Redirect back to the course list

    try:
        student_profile = user.student_profile
        student_department = student_profile.department
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Your student profile could not be found.')
        return redirect('course_list')

    if not student_department:
        messages.error(request, 'You are not assigned to a department and cannot enroll in courses.')
        return redirect('course_list')

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Check if the course belongs to the student's department
    if course.department != student_department:
        messages.error(request, f'This course is not available in your department ({student_department.department_name}).')
        return redirect('course_list')

    from courses.models import Enrollment
    try:
        # Create the enrollment record if it doesn't exist
        Enrollment.objects.get_or_create(student=user, course=course)
        messages.success(request, f'Successfully enrolled in {course.name}.')
    except Exception as e:
        messages.error(request, f'An error occurred during enrollment: {e}')

    return redirect('course_list') # Redirect back to the course list

@login_required
def drop_course_view(request, course_id):
    """
    Allow a student to drop a course.
    """
    # Ensure the logged-in user is a student
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to drop courses.')
        return redirect('course_list') # Redirect back to the course list

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    try:
        # Find and delete the enrollment record
        enrollment = CustomUser.objects.get(pk=request.user.id).courses_enrollments.get(course=course)
        enrollment.delete()
        messages.success(request, f'Successfully dropped {course.name}.')
    except CustomUser.DoesNotExist:
        messages.info(request, f'You are not enrolled in {course.name}.')
    except Exception as e:
        messages.error(request, f'An error occurred during dropping the course: {e}')

    return redirect('course_list') # Redirect back to the course list 

@login_required
def student_schedule_view(request):
    """
    Display the logged-in student's course schedule.
    """
    # Ensure the logged-in user is a student
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    student = request.user

    # Get the courses the student is enrolled in
    enrolled_courses = [enrollment.course for enrollment in student.courses_enrollments.all()]

    # Get the schedule entries for the enrolled courses
    # Using __in to filter schedules related to the list of enrolled courses
    student_schedule = CourseSchedule.objects.filter(course__in=enrolled_courses).order_by('day_of_week', 'start_time')

    # You might want to process the schedule data further here to group by day, etc.
    # For now, we'll pass the raw queryset.

    context = {
        'student': student,
        'student_schedule': student_schedule,
    }

    return render(request, 'courses/student_schedule.html', context)

@login_required
def student_grades_view(request):
    """
    Display the logged-in student's grades for assignments and exams.
    """
    # Ensure the logged-in user is a student
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    student = request.user

    # Get all assignment grades for the student
    assignment_grades = StudentAssignmentGrade.objects.filter(student=student).select_related('assignment', 'assignment__course').order_by('assignment__course__name', 'assignment__due_date')

    # Get all exam grades for the student
    exam_grades = StudentExamGrade.objects.filter(student=student).select_related('exam', 'exam__course').order_by('exam__course__name', 'exam__exam_date')

    context = {
        'student': student,
        'assignment_grades': assignment_grades,
        'exam_grades': exam_grades,
    }

    return render(request, 'courses/student_grades.html', context)

@login_required
def student_assignment_list_view(request):
    """
    Display assignments for the logged-in student's enrolled courses.
    """
    # Ensure the logged-in user is a student
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    student = request.user

    # Get the courses the student is enrolled in
    enrolled_course_ids = student.courses_enrollments.values_list('course__id', flat=True)

    # Get assignments for the enrolled courses
    assignments = Assignment.objects.filter(course__id__in=enrolled_course_ids).order_by('due_date')

    context = {
        'student': student,
        'assignments': assignments,
    }

    return render(request, 'courses/student_assignments.html', context)

@login_required
def student_exam_list_view(request):
    from django.utils import timezone
    import logging
    student = request.user
    logger = logging.getLogger(__name__)
    enrolled_course_ids = student.courses_enrollments.values_list('course__id', flat=True)
    logger.info(f"Student {student} enrolled in course IDs: {list(enrolled_course_ids)}")
    exams = Exam.objects.filter(
        course__id__in=enrolled_course_ids,
        exam_date__gte=timezone.now()
    ).order_by('exam_date')
    logger.info(f"Exams found for student: {[exam.title for exam in exams]}")
    return render(request, 'courses/student_exams.html', {'exams': exams})

@login_required
def student_payments_view(request):
    """
    Display the logged-in student's course payments and allow fake payment (mark as paid).
    """
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    student = request.user
    enrolled_courses = Course.objects.filter(enrollments__student=student)

    # Handle payment
    if request.method == 'POST' and 'pay_course_id' in request.POST:
        course_id = int(request.POST.get('pay_course_id'))
        course = Course.objects.get(course_id=course_id)
        payment = Payment.objects.filter(student=student, description__icontains=course.course_name, status='pending').first()
        if payment:
            payment.status = 'paid'
            payment.payment_date = timezone.now()
            payment.save()
            messages.success(request, 'Payment successful!')
        return redirect('courses:payments')

    # Build payment info for each enrolled course
    course_payments = []
    for course in enrolled_courses:
        payment = Payment.objects.filter(student=student, description__icontains=course.course_name).order_by('-payment_date').first()
        course_payments.append({
            'course': course,
            'payment': payment
        })

    return render(request, 'courses/student_payments.html', {'course_payments': course_payments})

@login_required
def submit_assignment_view(request, assignment_id):
    """
    Handle assignment submission for a logged-in student.
    """
    # Ensure the logged-in user is a student
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, 'You do not have permission to submit assignments.')
        return redirect('assignments') # Redirect back to the assignment list

    # Get the assignment object or return 404 if not found
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student = request.user

    # Check if the assignment is still open for submission
    if timezone.now() > assignment.due_date:
        messages.error(request, f'The due date for {assignment.title} has passed.')
        return redirect('assignments')

    # Check if the student has already submitted this assignment (based on unique_together)
    existing_submission = Submission.objects.filter(student=student, assignment=assignment).exists()
    if existing_submission:
         messages.info(request, f'You have already submitted {assignment.title}.')
         # Optionally, redirect to a view to see their submission or allow updating
         return redirect('assignments') # For now, just redirect back


    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES) # Include request.FILES for file uploads
        if form.is_valid():
            try:
                submission = form.save(commit=False)
                submission.student = student
                submission.assignment = assignment
                submission.save()
                messages.success(request, f'Successfully submitted {assignment.title}.')
                return redirect('assignments') # Redirect back to the assignment list
            except IntegrityError:
                 # This catch is less likely now with the explicit check above, but good for safety.
                 messages.info(request, f'You have already submitted {assignment.title}.')
            except Exception as e:
                messages.error(request, f'An error occurred during submission: {e}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = SubmissionForm()

    context = {
        'assignment': assignment,
        'form': form,
    }

    return render(request, 'courses/submit_assignment.html', context)

@login_required
def teacher_course_list_view(request):
    """
    Display a list of courses assigned to the logged-in teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user
    logger = logging.getLogger(__name__)
    logger.info(f"Teacher Course List View: Logged in user is {teacher.email} (Role: {teacher.role})")

    # Get courses assigned to the teacher
    assigned_courses = teacher.courses.all()
    logger.info(f"Teacher Course List View: Found {assigned_courses.count()} assigned courses.")

    context = {
        'teacher': teacher,
        'assigned_courses': assigned_courses,
    }

    return render(request, 'courses/teacher_course_list.html', context)

@login_required
def create_assignment_view(request, course_id):
    """
    Allow a teacher to create a new assignment for their assigned course.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to create assignments.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, 'You are not assigned to this course.')
        return redirect('teacher_course_list') # Redirect back to the teacher's course list

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course # Link the assignment to the course
            assignment.save()
            messages.success(request, f'Assignment "{assignment.title}" created successfully for {course.name}.')
            # Redirect to a page showing the course assignments or the course details page
            # We'll need a view for listing assignments for a specific course next.
            return redirect('teacher_course_list') # Redirect back to the teacher's course list for now
    else:
        form = AssignmentForm()

    context = {
        'course': course,
        'form': form,
    }

    return render(request, 'courses/create_assignment.html', context)

@login_required
def teacher_assignment_list_view(request, course_id):
    """
    Display a list of assignments for a specific course, for the assigned teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, 'You are not assigned to this course.')
        return redirect('teacher_course_list') # Redirect back to the teacher's course list

    # Get assignments for this course, ordered by due date
    assignments = Assignment.objects.filter(course=course).order_by('due_date')

    context = {
        'teacher': teacher,
        'course': course,
        'assignments': assignments,
    }

    return render(request, 'courses/teacher_assignment_list.html', context)

@login_required
def teacher_submission_list_view(request, assignment_id):
    """
    Display a list of submissions for a specific assignment, for the assigned teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the assignment object or return 404 if not found
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    # Ensure the teacher is assigned to the course this assignment belongs to
    if assignment.course.teacher != teacher:
        messages.error(request, f'You are not assigned to the course for this assignment ({assignment.course.name}).')
        return redirect('teacher_course_list') # Redirect back to the teacher's course list

    # Get submissions for this assignment
    submissions = Submission.objects.filter(assignment=assignment).select_related('student').order_by('submitted_at')

    # You might also want to fetch existing grades for these submissions
    submission_grades = StudentAssignmentGrade.objects.filter(assignment=assignment).values('student__id', 'grade')
    # Create a dictionary for easy lookup of grades by student ID
    grades_dict = {grade['student__id']: grade['grade'] for grade in submission_grades}

    context = {
        'teacher': teacher,
        'assignment': assignment,
        'submissions': submissions,
        'grades_dict': grades_dict,
    }

    return render(request, 'courses/teacher_submission_list.html', context)

@login_required
def teacher_enrolled_students_view(request, course_id):
    """
    Display a list of students enrolled in a specific course for the assigned teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to this course ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    # Get students enrolled in this course
    # Use select_related to fetch student details efficiently
    enrolled_students = CustomUser.objects.filter(courses_enrollments__course=course, courses_enrollments__student__role='student') \
                                          .select_related('courses_enrollments') \
                                          .order_by('name') # Order students by name

    context = {
        'teacher': teacher,
        'course': course,
        'enrolled_students': enrolled_students,
    }

    return render(request, 'courses/teacher_enrolled_students.html', context)

@login_required
def mark_attendance_view(request, session_id):
    """
    Allow a teacher to mark attendance for a specific session.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the session object or return 404, select related course
    session = get_object_or_404(Session.objects.select_related('course'), pk=session_id)
    course = session.course

    # Ensure the teacher is assigned to the course for this session
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to the course for this session ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    # Get all students enrolled in this course
    enrolled_students = CustomUser.objects.filter(courses_enrollments__course=course, courses_enrollments__student__role='student').order_by('name')

    # Create a formset factory for the Attendance model, related to the current session
    # We will create forms for existing attendance records or initial forms for enrolled students.

    # Method 1: Using modelformset_factory to manage Attendance records directly
    # This requires pre-creating Attendance objects or handling the 'extra' forms.

    # Method 2 (Simpler): Create forms for each enrolled student manually or use a custom formset.
    # Let's use modelformset_factory but prepare initial data.

    # Get existing attendance records for this session
    existing_attendance = Attendance.objects.filter(session=session)

    # Create a dictionary of existing attendance records by student ID for easy lookup
    existing_attendance_dict = {att.student_id: att for att in existing_attendance}

    # Prepare initial data for students who don't have an attendance record yet for this session
    # This ensures all enrolled students appear in the formset.
    initial_data = []
    for student in enrolled_students:
        if student.id not in existing_attendance_dict:
            initial_data.append({'student': student, 'session': session, 'status': 'absent'}) # Default to absent

    # Create a ModelFormSet factory for Attendance records
    # Use queryset to include only existing records for this session
    # initial adds forms for students without existing records
    # We need to exclude 'session' from fields and handle it in the view to avoid users changing it.
    AttendanceModelFormSet = modelformset_factory(Attendance, form=AttendanceForm, extra=len(initial_data), can_delete=False)
    # Note: 'student' is not in AttendanceForm fields, we need to handle displaying student name and linking form to student.
    # Let's create a custom form that includes student information.

    # Refined Approach: Custom Form with Student Info + Formset Factory
    class BaseMarkAttendanceFormSet(BaseFormSet):
        def get_form_kwargs(self, index):
             kwargs = super().get_form_kwargs(index)
             kwargs['session'] = session # Pass session to the form
             kwargs['student'] = self.initial_form_data[index]['student'] # Pass student instance
             return kwargs

    class MarkAttendanceForm(forms.ModelForm):
        student_name = forms.CharField(max_length=255, disabled=True, required=False)

        class Meta:
            model = Attendance
            fields = ['status']
            # We will link student and session in the view or formset save method

        def __init__(self, *args, **kwargs):
            self.session = kwargs.pop('session', None)
            self.student = kwargs.pop('student', None)
            super().__init__(*args, **kwargs)
            if self.student:
                self.fields['student_name'].initial = self.student.name

    # Prepare initial data with student and existing status
    initial_form_data = []
    for student in enrolled_students:
        initial_data_item = {'student': student}
        if student.id in existing_attendance_dict:
            initial_data_item['status'] = existing_attendance_dict[student.id].status
            initial_data_item['id'] = existing_attendance_dict[student.id].id # Include ID for existing records
        else:
            initial_data_item['status'] = 'absent' # Default status
        initial_form_data.append(initial_data_item)

    MarkAttendanceFormSet = formset_factory(MarkAttendanceForm, formset=BaseMarkAttendanceFormSet, extra=0) # Set extra to 0 as we provide initial data


    if request.method == 'POST':
        # Use the existing attendance records as the queryset for saving, to update instead of create new ones if they exist.
        # We need to handle mapping form data back to students and sessions.
        # A model formset is better for saving, let's rethink the formset approach.

        # Let's go back to inlineformset_factory but handle the creation of initial Attendance objects if they don't exist.
        # First, ensure all enrolled students have an Attendance object for this session.
        for student in enrolled_students:
            Attendance.objects.get_or_create(
                session=session,
                student=student,
                defaults={'status': 'absent'} # Create with default status if not exists
            )

        # Now use inlineformset_factory to edit these potentially newly created or existing records.
        AttendanceFormSet = inlineformset_factory(Session, Attendance, fields=['student', 'status'], extra=0, can_delete=False, form=AttendanceForm)
        # Exclude student from the form fields as it's handled by the formset instance implicitly.
        # We need to make sure the formset only deals with Attendance records for the current session.
        # The queryset for inlineformset_factory is typically filtered by the parent instance.
        # Let's make sure the form only allows editing the status.

        class SimpleAttendanceForm(forms.ModelForm):
             class Meta:
                model = Attendance
                fields = ['status']

        AttendanceInlineFormSet = inlineformset_factory(Session, Attendance, form=SimpleAttendanceForm, extra=0, can_delete=False)

        formset = AttendanceInlineFormSet(request.POST, instance=session) # Pass the session instance

        # Need to ensure the formset only includes forms for students enrolled in the course.
        # The inline formset automatically filters by session due to the instance argument.
        # We need to make sure it only creates/updates records for students enrolled in the course.
        # The get_or_create step above ensures all enrolled students have an attendance object for this session.

        if formset.is_valid():
            formset.save()
            messages.success(request, f'Attendance for {course.name} session on {session.date} marked successfully.')
            return redirect('courses:teacher_session_list', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors in the formset.')
            # Fall through to render with errors

    else:
        # On GET request, ensure all enrolled students have an Attendance object for this session (create if not exists)
        for student in enrolled_students:
            Attendance.objects.get_or_create(
                session=session,
                student=student,
                defaults={'status': 'absent'} # Create with default status if not exists
            )

        # Use inlineformset_factory to get forms for existing attendance records related to the session
        class SimpleAttendanceForm(forms.ModelForm):
             class Meta:
                model = Attendance
                fields = ['status']

        AttendanceInlineFormSet = inlineformset_factory(Session, Attendance, form=SimpleAttendanceForm, extra=0, can_delete=False)

        formset = AttendanceInlineFormSet(instance=session) # Pass the session instance to filter attendance records
        # The formset now contains forms for each Attendance object related to this session.
        # Each form instance will have an associated Attendance object, which in turn has a student and a status.
        # We need to access the student from the form's instance to display student name in the template.


    context = {
        'teacher': teacher,
        'course': course,
        'session': session,
        'formset': formset,
    }

    return render(request, 'courses/mark_attendance.html', context)

@login_required
def teacher_attendance_history_view(request, course_id):
    """
    Display attendance history for students in a specific course, for the assigned teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to this course ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    # Get all sessions for this course
    sessions = Session.objects.filter(course=course).order_by('date', 'start_time')

    # Get all attendance records for these sessions, related to enrolled students
    # This might be inefficient for many students/sessions. Consider optimizations if needed.
    attendance_records = Attendance.objects.filter(session__in=sessions).select_related('student', 'session').order_by('student__name', 'session__date', 'session__start_time')

    # Structure data for template: dictionary keyed by student, with a list of attendance records
    attendance_by_student = {}
    for record in attendance_records:
        if record.student not in attendance_by_student:
            attendance_by_student[record.student] = []
        attendance_by_student[record.student].append(record)

    context = {
        'teacher': teacher,
        'course': course,
        'sessions': sessions, # Pass sessions to display dates/times
        'attendance_by_student': attendance_by_student,
    }

    return render(request, 'courses/teacher_attendance_history.html', context)

@login_required
def teacher_exam_list_view(request, course_id):
    """
    Display a list of exams for a specific course, for the assigned teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to this course ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    # Get exams for this course, ordered by exam date
    exams = Exam.objects.filter(course=course).order_by('exam_date')

    context = {
        'teacher': teacher,
        'course': course,
        'exams': exams,
    }

    return render(request, 'courses/teacher_exam_list.html', context)

@login_required
def teacher_exam_students_list_view(request, exam_id):
    """
    Display a list of students for a specific exam, for the assigned teacher, to facilitate grading.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the exam object or return 404, select related course
    exam = get_object_or_404(Exam.objects.select_related('course'), pk=exam_id)
    course = exam.course

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to the course for this exam ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    # Get all students enrolled in this course
    enrolled_students = CustomUser.objects.filter(courses_enrollments__course=course, courses_enrollments__student__role='student').order_by('name')

    # Get existing exam grades for this exam for the enrolled students
    existing_grades = StudentExamGrade.objects.filter(exam=exam, student__in=enrolled_students).values('student__id', 'grade')
    grades_dict = {grade['student__id']: grade['grade'] for grade in existing_grades}

    context = {
        'teacher': teacher,
        'exam': exam,
        'enrolled_students': enrolled_students,
        'grades_dict': grades_dict, # Pass existing grades to display in the list
    }

    return render(request, 'courses/teacher_exam_students_list.html', context)

@login_required
def create_exam_view(request, course_id):
    """
    Allow a teacher to create a new exam for their assigned course.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to create exams.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, 'You are not assigned to this course.')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.course = course # Link the exam to the course
            exam.save()
            messages.success(request, f'Exam "{exam.title}" created successfully for {course.name}.')
            # Redirect to the exam list for this course
            return redirect('courses:teacher_exam_list', course_id=course.id)
    else:
        form = ExamForm()

    context = {
        'course': course,
        'form': form,
    }

    return render(request, 'courses/create_exam.html', context)

@login_required
def edit_exam_view(request, exam_id):
    """
    Allow a teacher to edit an existing exam.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to edit exams.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the exam object or return 404, select related course
    exam = get_object_or_404(Exam.objects.select_related('course'), pk=exam_id)
    course = exam.course

    # Ensure the teacher is assigned to the course for this exam
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to the course for this exam ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exam "{exam.title}" updated successfully for {course.name}.')
            # Redirect to the exam list for this course
            return redirect('courses:teacher_exam_list', course_id=course.id)
    else:
        form = ExamForm(instance=exam) # Pre-fill form with existing exam data

    context = {
        'exam': exam,
        'course': course,
        'form': form,
    }

    return render(request, 'courses/edit_exam.html', context)

@login_required
def delete_exam_view(request, exam_id):
    """
    Allow a teacher to delete an existing exam.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to delete exams.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the exam object or return 404, select related course
    exam = get_object_or_404(Exam.objects.select_related('course'), pk=exam_id)
    course = exam.course

    # Ensure the teacher is assigned to the course for this exam
    if course.teacher != teacher:
        messages.error(request, f'You are not assigned to the course for this exam ({course.name}).')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    if request.method == 'POST':
        exam.delete()
        messages.success(request, f'Exam "{exam.title}" for {course.name} deleted successfully.')
        # Redirect to the exam list for this course after deletion
        return redirect('courses:teacher_exam_list', course_id=course.id)

    # For GET request, show a confirmation page
    context = {
        'exam': exam,
        'course': course,
    }

    return render(request, 'courses/confirm_delete_exam.html', context)

@login_required
def grade_submission_view(request, submission_id):
    """
    Allow a teacher to grade a student's assignment submission.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to grade submissions.')
        return redirect('home') # Redirect to home or a permission denied page

    # Placeholder logic - replace with actual grading functionality
    messages.info(request, f'Placeholder for grading submission {submission_id}.')

    # Redirect to the submission list for the relevant assignment or another appropriate page
    # You'll need to determine the assignment_id from the submission_id.
    # For now, redirecting to teacher's course list as a fallback.
    return redirect('courses:teacher_course_list')

@login_required
def teacher_session_list_view(request, course_id):
    user = request.user
    course = get_object_or_404(Course, course_id=course_id)
    if not (user.role == 'teacher' and course.teacher == user) and not user.role == 'admin':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('courses:teacher_course_list')
    sessions = CourseSchedule.objects.filter(course=course).order_by('day_of_week', 'start_time')
    return render(request, 'courses/teacher_session_list.html', {'course': course, 'sessions': sessions})

@login_required
def create_session_view(request, course_id):
    user = request.user
    course = get_object_or_404(Course, course_id=course_id)
    if not (user.role == 'teacher' and course.teacher == user) and not user.role == 'admin':
        messages.error(request, "You do not have permission to add sessions.")
        return redirect('courses:teacher_course_list')
    if request.method == 'POST':
        form = CourseScheduleForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.course = course
            session.save()
            messages.success(request, "Session added!")
            return redirect('courses:teacher_session_list', course_id=course_id)
    else:
        form = CourseScheduleForm()
    return render(request, 'courses/create_session.html', {'form': form, 'course': course})

@login_required
def grade_exam_view(request, exam_id, student_id):
    """
    Allow a teacher to grade a student's exam.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to grade exams.')
        return redirect('home') # Redirect to home or a permission denied page

    # Placeholder logic - replace with actual grading functionality
    messages.info(request, f'Placeholder for grading exam {exam_id} for student {student_id}.')

    # Redirect to the list of students for the exam or another appropriate page
    # You'll need to determine the exam_id and student_id from the URL.
    # For now, redirecting to the exam students list.
    return redirect('courses:teacher_exam_students_list', exam_id=exam_id)

@login_required
def teacher_all_attendance_view(request):
    """
    Display an overview of attendance for all courses assigned to the logged-in teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the IDs of the courses assigned to the teacher
    assigned_course_ids = teacher.courses.values_list('id', flat=True)

    # Get all sessions for these courses
    all_sessions = Session.objects.filter(course__id__in=assigned_course_ids).order_by('course__name', 'date', 'start_time')

    # Get all attendance records for these sessions, including student and session details
    # This could be a large query; consider pagination or filtering if performance is an issue.
    all_attendance_records = Attendance.objects.filter(session__in=all_sessions).select_related('student', 'session__course').order_by('session__course__name', 'session__date', 'student__name')

    # To display this effectively, we might group by course or student.
    # Let's group by course for the overview.
    attendance_by_course = {}
    for record in all_attendance_records:
        course_name = record.session.course.name
        if course_name not in attendance_by_course:
            attendance_by_course[course_name] = []
        attendance_by_course[course_name].append(record)

    context = {
        'teacher': teacher,
        'attendance_by_course': attendance_by_course,
    }

    return render(request, 'courses/teacher_all_attendance.html', context)

@login_required
def teacher_all_assignments_view(request):
    """
    Display a list of all assignments for all courses assigned to the logged-in teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the IDs of the courses assigned to the teacher
    assigned_course_ids = teacher.courses.values_list('id', flat=True)

    # Get all assignments for these courses
    all_assignments = Assignment.objects.filter(course__id__in=assigned_course_ids).order_by('course__name', 'due_date')

    context = {
        'teacher': teacher,
        'all_assignments': all_assignments,
    }

    return render(request, 'courses/teacher_all_assignments.html', context)

@login_required
def teacher_all_exams_view(request):
    teacher = request.user
    assigned_course_ids = teacher.courses.values_list('id', flat=True)
    exams = Exam.objects.filter(course__id__in=assigned_course_ids).order_by('exam_date')
    return render(request, 'courses/teacher_all_exams.html', {'exams': exams})

@login_required
def teacher_all_grades_view(request):
    """
    Display an overview of grades for all students in all courses assigned to the logged-in teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the IDs of the courses assigned to the teacher
    assigned_course_ids = teacher.courses.values_list('id', flat=True)

    # Get all students enrolled in these courses
    # Use distinct() to avoid duplicate students if they are in multiple courses taught by the same teacher
    all_students = CustomUser.objects.filter(
        courses_enrollments__course__id__in=assigned_course_ids,
        courses_enrollments__student__role='student'
    ).distinct().order_by('name')

    # Fetch all assignment and exam grades for these students in these courses
    assignment_grades = StudentAssignmentGrade.objects.filter(
        student__in=all_students,
        assignment__course__id__in=assigned_course_ids
    ).select_related('student', 'assignment__course', 'assignment')

    exam_grades = StudentExamGrade.objects.filter(
        student__in=all_students,
        exam__course__id__in=assigned_course_ids
    ).select_related('student', 'exam__course', 'exam')

    # Structure data for template: dictionary keyed by student, with lists of their assignment and exam grades
    grades_by_student = {}
    for student in all_students:
        grades_by_student[student] = {
            'assignment_grades': [],
            'exam_grades': [],
        }

    for assignment_grade in assignment_grades:
        grades_by_student[assignment_grade.student]['assignment_grades'].append(assignment_grade)

    for exam_grade in exam_grades:
        grades_by_student[exam_grade.student]['exam_grades'].append(exam_grade)

    context = {
        'teacher': teacher,
        'grades_by_student': grades_by_student,
    }

    return render(request, 'courses/teacher_all_grades.html', context)

@login_required
def teacher_course_material_list_view(request, course_id):
    """
    Display a list of course materials for a specific course, for the assigned teacher.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, 'You are not assigned to this course.')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    # Get all materials for this course
    materials = CourseMaterial.objects.filter(course=course).order_by('-uploaded_at')

    context = {
        'teacher': teacher,
        'course': course,
        'materials': materials,
    }

    return render(request, 'courses/teacher_course_material_list.html', context)

@login_required
def teacher_upload_course_material_view(request, course_id):
    """
    Allow a teacher to upload new course material for their assigned course.
    """
    # Ensure the logged-in user is a teacher
    if not hasattr(request.user, 'role') or request.user.role != 'teacher':
        messages.error(request, 'You do not have permission to upload materials.')
        return redirect('home') # Redirect to home or a permission denied page

    teacher = request.user

    # Get the course object or return 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Ensure the teacher is assigned to this course
    if course.teacher != teacher:
        messages.error(request, 'You are not assigned to this course.')
        return redirect('courses:teacher_course_list') # Redirect back to the teacher's course list

    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES) # Include request.FILES for file uploads
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course # Link the material to the course
            material.save()
            messages.success(request, f'Material "{material.title}" uploaded successfully for {course.name}.')
            return redirect('courses:teacher_course_material_list', course_id=course.id) # Redirect to the materials list for the course
    else:
        form = CourseMaterialForm()

    context = {
        'course': course,
        'form': form,
    }

    return render(request, 'courses/teacher_upload_course_material.html', context)

@login_required
def fake_payment_gateway_view(request, course_id):
    student = request.user
    course = get_object_or_404(Course, course_id=course_id)
    payment = Payment.objects.filter(
        student=student,
        description=f"Course Fee: {course.course_name}",
        status='pending'
    ).first()
    if not payment:
        messages.error(request, "No pending payment found for this course.")
        return redirect('courses:payments')

    if request.method == 'POST':
        # Here you could validate fake card info, etc.
        payment.status = 'paid'
        payment.payment_date = timezone.now()
        payment.save()
        messages.success(request, "Payment successful!")
        return redirect('courses:payments')

    return render(request, 'courses/fake_payment_gateway.html', {'course': course, 'payment': payment})

class CourseScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'location']