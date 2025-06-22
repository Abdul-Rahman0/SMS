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
# admin.site.register(AdminProfile)
# admin.site.register(TeacherProfile)
# admin.site.register(StudentProfile)

# Keep registrations for other models
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Exam)
admin.site.register(ExamSchedule)
admin.site.register(ExamResult)
# admin.site.register(Attendance)
admin.site.register(Assignment)
# admin.site.register(Payment)
# admin.site.register(StudentCourseSchedule)
admin.site.register(CourseWork)
admin.site.register(ContactMessage) # Register ContactMessage as well



from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model



User = get_user_model()
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ('course_name', 'credits', 'teacher', 'department')  # optional

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            try:
                teacher_group = Group.objects.get(name="Teacher")
                kwargs["queryset"] = User.objects.filter(groups=teacher_group)
            except Group.DoesNotExist:
                kwargs["queryset"] = User.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(TeacherProfile)
class TeacherAdmin(admin.ModelAdmin):
    model = Course
    list_display = ('user', 'department', "specialization")  # optional

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            try:
                teacher_group = Group.objects.get(name="Teacher")
                kwargs["queryset"] = User.objects.filter(groups=teacher_group)
            except Group.DoesNotExist:
                kwargs["queryset"] = User.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):
    model = StudentProfile
    list_display = ('user', 'enrollment_date', 'department', 'get_courses')  # use custom method

    def get_courses(self, obj):
        return ", ".join([course.course_name for course in obj.courses.all()])
    get_courses.short_description = 'Courses'  # Column header name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            try:
                teacher_group = Group.objects.get(name="Student")
                kwargs["queryset"] = User.objects.filter(groups=teacher_group)
            except Group.DoesNotExist:
                kwargs["queryset"] = User.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    model = Attendance
    list_display = ("attendance_id","student","course","status","date")  # use custom method

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            if request.user.is_superuser:
                try:
                    student_group = Group.objects.get(name="Student")
                    kwargs["queryset"] = User.objects.filter(groups=student_group)
                except Group.DoesNotExist:
                    kwargs["queryset"] = User.objects.none()
            else:
                # Agar user student hai to sirf apna hi record dekhe
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(Payment)
class PaymenteAdmin(admin.ModelAdmin):
    model = Payment

    list_display = ("student","amount","date","status")  # use custom method

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            if request.user.is_superuser:
                try:
                    student_group = Group.objects.get(name="Student")
                    kwargs["queryset"] = User.objects.filter(groups=student_group)
                except Group.DoesNotExist:
                    kwargs["queryset"] = User.objects.none()
            else:
                # Agar user student hai to sirf apna hi record dekhe
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StudentCourseSchedule)
class StudentCourseScheduleAdmin(admin.ModelAdmin):
    model = StudentCourseSchedule

    list_display = ("student","course","day","time")  # use custom method

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            if request.user.is_superuser:
                try:
                    student_group = Group.objects.get(name="Student")
                    kwargs["queryset"] = User.objects.filter(groups=student_group)
                except Group.DoesNotExist:
                    kwargs["queryset"] = User.objects.none()
            else:
                # Agar user student hai to sirf apna hi record dekhe
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.site_header = 'Student Management System Admin'
admin.site.site_title = 'Student Management System Admin Portal'
admin.site.index_title = 'Welcome to the Student Management System Admin' 