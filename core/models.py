from django.db import models
from django.utils import timezone
from django.conf import settings

# Department
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=255)
    head_of_department = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='core_headed_departments', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.department_name

# Admin Profile (inherits from models.Model and links to CustomUser)
class AdminProfile(models.Model):
    # Link to the CustomUser model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')
    # Add Admin-specific fields here if any (admin_id was on the old Admin, but OneToOneField PK replaces it)
    # Example: admin_specific_field = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'admin profile'
        verbose_name_plural = 'admin profiles'

    def __str__(self):
        return f"Admin Profile for {self.user.email}"

    # Admin methods (consider if these should be on the CustomUser or the profile)
    # For now, keeping placeholder methods on the profile as per your initial structure
    def add_student(self, student_data): pass
    def remove_student(self, student_id): pass
    def add_teacher(self, teacher_data): pass
    def remove_teacher(self, teacher_id): pass
    def assign_course(self, teacher_id, course_id): pass
    def view_all_users(self): pass

# Teacher Profile (inherits from models.Model and links to CustomUser)
class TeacherProfile(models.Model):
    # Link to the CustomUser model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='teacher_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    specialization = models.CharField(max_length=255, null=True, blank=True) # Added null/blank as per typical usage

    class Meta:
        verbose_name = 'teacher profile'
        verbose_name_plural = 'teacher profiles'

    def __str__(self):
        return f"Teacher Profile for {self.user.email}"

    # Teacher methods (consider if these should be on the CustomUser or the profile)
    def create_assignment(self, course_id, assignment_details): pass
    def grade_assignment(self, student_id, assignment_id, grade): pass
    def mark_attendance(self, student_id, status): pass
    def view_assigned_courses(self): pass

# Course
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    course_description = models.TextField(null=True, blank=True)
    credits = models.IntegerField(null=True, blank=True) # Added null/blank
    # ForeignKey to the CustomUser who is a teacher
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='taught_courses')
    # ForeignKey to Department
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='courses')

    def __str__(self):
        return self.course_name

    # Course methods
    def add_course(self, course_data): pass
    def remove_course(self, course_id): pass
    def view_students(self, course_id): pass

# Student Profile (inherits from models.Model and links to CustomUser)
class StudentProfile(models.Model):
    # Link to the CustomUser model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    enrollment_date = models.DateField(default=timezone.now) # Added default
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    # ManyToManyField to Course - related_name 'enrolled_students' to avoid clash
    courses = models.ManyToManyField(Course, related_name='enrolled_students', blank=True) # Renamed course_list to courses, added blank=True

    class Meta:
        verbose_name = 'student profile'
        verbose_name_plural = 'student profiles'

    def __str__(self):
        return f"Student Profile for {self.user.email}"

    # Student methods (consider if these should be on the CustomUser or the profile)
    def enroll_course(self, course_id): pass
    def drop_course(self, course_id): pass
    def view_schedule(self): pass
    def view_grades(self): pass
    def submit_assignment(self, assignment_id, file): pass

# Exam
class Exam(models.Model):
    exam_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams') # Added related_name
    date = models.DateField()
    duration = models.IntegerField()  # in minutes
    total_marks = models.IntegerField()

    def schedule_exam(self, course_id, date, duration): pass
    def view_exam_details(self, exam_id): pass
    def grade_exam(self, student_id, marks): pass

# Exam Schedule
class ExamSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules') # Added related_name
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)

    def add_exam_schedule(self, exam_id, date, start_time, end_time, location): pass
    def update_exam_schedule(self, schedule_id, new_date, new_time, new_location): pass
    def view_exam_schedule(self, exam_id): pass

# Exam Results
class ExamResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    # ForeignKey to the CustomUser who is a student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.IntegerField()
    grade = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'exam result'
        verbose_name_plural = 'exam results'
        unique_together = ('student', 'exam') # Ensure one result per student per exam

    def view_results(self, student_id): pass
    def update_results(self, result_id, marks): pass

# Attendance
class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    # ForeignKey to the CustomUser who is a student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records') # Changed related_name
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records') # Added related_name
    status = models.CharField(max_length=10, choices=(('Present', 'Present'), ('Absent', 'Absent')))
    date = models.DateField()

    class Meta:
        unique_together = ('student', 'course', 'date') # Ensure one attendance record per student per course per day

    def mark_attendance(self, student_id, status): pass
    def view_attendance(self, student_id): pass

# Assignment
class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments') # Added related_name
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)

    class Meta:
        verbose_name = 'assignment'
        verbose_name_plural = 'assignments'

    def create_assignment(self, course_id, title, description, due_date): pass
    def submit_assignment(self, student_id, file): pass
    def grade_assignment(self, student_id, assignment_id, marks): pass

# Payment
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    # ForeignKey to the CustomUser who is a student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_payments')
    amount = models.FloatField()
    date = models.DateField()
    status = models.CharField(max_length=10, choices=(('Paid', 'Paid'), ('Pending', 'Pending')))

    class Meta:
        verbose_name = 'payment'
        verbose_name_plural = 'payments'

    def process_payment(self, student_id, amount): pass
    def view_payment_history(self, student_id): pass

# Student Course Schedule
class StudentCourseSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    # ForeignKey to the CustomUser who is a student
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_schedules')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    time = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'student course schedule'
        verbose_name_plural = 'student course schedules'
        unique_together = ('student', 'course', 'day', 'time') # Ensure unique schedule entries

    def view_student_schedule(self, student_id): pass
    def update_schedule(self, student_id, course_id, new_time): pass

# Course Work
class CourseWork(models.Model):
    course_work_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_work') # Added related_name
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateField()
    points = models.IntegerField(null=True, blank=True) # Added null/blank

    class Meta:
        verbose_name = 'course work'
        verbose_name_plural = 'course work'

    def add_course_work(self, course_id, title, description, due_date, points): pass
    def update_course_work(self, course_work_id, title, description, due_date, points): pass
    def view_course_work(self, course_id): pass
    def submit_course_work(self, student_id, course_work_id, submission_date): pass
    def grade_course_work(self, course_work_id, student_id, grade): pass

# Contact Message
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'contact message'
        verbose_name_plural = 'contact messages'

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

# Enrollment Model (intermediary for ManyToMany relationship between CustomUser and Course)
class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course') # Ensure a student can only enroll in a course once
        verbose_name = 'enrollment'
        verbose_name_plural = 'enrollments'

    def __str__(self):
        return f'{self.student.email} enrolled in {self.course.course_name}' 