from django.contrib import admin
from .models import (
    # Remove User and old Admin, Student, Teacher imports
    # User, Admin, Student, Teacher,
    Department, Course, Exam, ExamSchedule,
    ExamResult, Attendance, Assignment, Payment, StudentCourseSchedule, CourseWork,
    # Import the new profile models
    AdminProfile, TeacherProfile, StudentProfile,
    # Also import ContactMessage if you want to register it
    ContactMessage,
)

# Remove old registrations for User, Admin, Student, Teacher
# admin.site.register(User)
# admin.site.register(Admin)
# admin.site.register(Student)
# admin.site.register(Teacher)

# Register the new profile models
admin.site.register(AdminProfile)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)

# Keep registrations for other models
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Exam)
admin.site.register(ExamSchedule)
admin.site.register(ExamResult)
admin.site.register(Attendance)
admin.site.register(Assignment)
admin.site.register(Payment)
admin.site.register(StudentCourseSchedule)
admin.site.register(CourseWork)
admin.site.register(ContactMessage) # Register ContactMessage as well

admin.site.site_header = 'Student Management System Admin'
admin.site.site_title = 'Student Management System Admin Portal'
admin.site.index_title = 'Welcome to the Student Management System Admin' 