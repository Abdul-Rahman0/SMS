from django.db import models
from users.models import CustomUser
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=255)
    head_of_department = models.ForeignKey(CustomUser, related_name='courses_headed_departments', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    admin = models.ForeignKey(CustomUser, related_name='admin_departments', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'admin'})

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    credits = models.IntegerField()
    teacher = models.ForeignKey(CustomUser, related_name='courses', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    """
    Represents a student's enrollment in a course.
    """
    student = models.ForeignKey(CustomUser, related_name='courses_enrollments', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(default=timezone.now)

    class Meta:
        # Ensure a student can only enroll in a course once
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student.name} enrolled in {self.course.name}'

class CourseSchedule(models.Model):
    """
    Represents the schedule details for a specific course session.
    """
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    course = models.ForeignKey(Course, related_name='schedules', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('course', 'day_of_week', 'start_time') # Prevent duplicate schedules for the same course/day/time

    def __str__(self):
        return f'{self.course.name} on {self.day_of_week} ({self.start_time}-{self.end_time})'

class Assignment(models.Model):
    """
    Represents an assignment for a course.
    """
    course = models.ForeignKey(Course, related_name='assignments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assignments_created',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.title} for {self.course.name}'

class Exam(models.Model):
    """
    Represents an exam for a course.
    """
    course = models.ForeignKey(Course, related_name='exams', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exam_date = models.DateTimeField()

    def __str__(self):
        return f'{self.title} for {self.course.name}'

class StudentAssignmentGrade(models.Model):
    """
    Stores a student's grade for a specific assignment.
    """
    student = models.ForeignKey(CustomUser, related_name='assignment_grades', on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, related_name='grades', on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Grade can be null if not yet graded

    class Meta:
        unique_together = ('student', 'assignment')

    def __str__(self):
        return f'{self.student.name} - {self.assignment.title}: {self.grade}'

class StudentExamGrade(models.Model):
    """
    Stores a student's grade for a specific exam.
    """
    student = models.ForeignKey(CustomUser, related_name='exam_grades', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, related_name='grades', on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Grade can be null if not yet graded

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f'{self.student.name} - {self.exam.title}: {self.grade}'

class Payment(models.Model):
    """
    Represents a payment made by a student.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(CustomUser, related_name='courses_payments', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True, null=True) # e.g., 'Tuition Fee', 'Library Fine'

    class Meta:
        ordering = ['-payment_date'] # Order by newest payments first

    def __str__(self):
        return f'Payment of {self.amount} by {self.student.name} - {self.status}'

class Submission(models.Model):
    """
    Represents a student's submission for an assignment.
    """
    student = models.ForeignKey(CustomUser, related_name='submissions', on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, related_name='submissions', on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignments/submissions/') # Files will be uploaded to media/assignments/submissions/
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a student can only submit to an assignment once (or you might allow multiple and track versions)
        # For simplicity, let's assume one submission per student per assignment for now.
        unique_together = ('student', 'assignment')
        ordering = ['submitted_at']

    def __str__(self):
        return f'Submission by {self.student.name} for {self.assignment.title}'

class Session(models.Model):
    """
    Represents a specific course session on a given date and time.
    """
    course = models.ForeignKey(Course, related_name='sessions', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('course', 'date', 'start_time') # Prevent duplicate sessions for the same course/date/time

    def __str__(self):
        return f'{self.course.name} on {self.date} at {self.start_time}'

class Attendance(models.Model):
    """
    Records a student's attendance for a specific session.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'), # Optional: Add an excused status
    ]

    session = models.ForeignKey(Session, related_name='attendance', on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, related_name='attendance', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recorded_at = models.DateTimeField(auto_now_add=True) # When the attendance was recorded

    class Meta:
        unique_together = ('session', 'student') # Ensure a student has only one attendance record per session

    def __str__(self):
        return f'{self.student.name} - {self.session.course.name} ({self.session.date}): {self.status}'

# New model for Course Materials
class CourseMaterial(models.Model):
    """
    Represents course material uploaded by a teacher.
    """
    course = models.ForeignKey(Course, related_name='materials', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='course_materials/') # Files will be uploaded to media/course_materials/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at'] # Order by newest materials first

    def __str__(self):
        return f'{self.title} for {self.course.name}'