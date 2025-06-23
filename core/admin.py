from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import AssignmentSubmitForm
from .models import (
    # Remove User and old Admin, Student, Teacher imports
    # User, Admin, Student, Teacher,
    Department, Course, Exam, ExamSchedule,
    ExamResult, Attendance, Assignment, Payment, StudentCourseSchedule, CourseWork, AssignmentSubmit, Assignmentgrade,
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
# admin.site.register(Course)
admin.site.register(Exam)
admin.site.register(ExamSchedule)
admin.site.register(ExamResult)
# admin.site.register(Attendance)
# admin.site.register(Assignment)
# admin.site.register(Payment)
# admin.site.register(StudentCourseSchedule)
admin.site.register(CourseWork)
admin.site.register(ContactMessage) # Register ContactMessage as well



from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model



User = get_user_model()



@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    fields=( 'course','title', 'description','due_date')
    list_display = ('course','title', 'description')
    search_fields = ('description',)
    list_filter = ('due_date',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set on create
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

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


@admin.register(AssignmentSubmit)
class AssignmentSubmitAdmin(admin.ModelAdmin):
    form = AssignmentSubmitForm
    fields = ('file', 'description', 'due_date', 'assigment')  # show only these fields in form
    list_display = ('assigment','submitted_by', 'due_date', 'description')
    search_fields = ('description',)
    list_filter = ('due_date',)
    def get_fields(self, request, obj=None):
        fields = ['file', 'description', 'due_date', 'assigment']
        if obj:
            if obj.assigment.created_by == request.user:
                fields.append('marks')  # Teacher: editable
            elif obj.marks:
                fields.append('marks')  # Student: read-only
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly = []
        if obj:
            if obj.marks and obj.assigment.created_by != request.user:
                readonly.append('marks')  # Student can't edit marks
        return readonly


    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # ✅ Superuser can see all
        if request.user.is_superuser:
            return qs

        # ✅ Teacher (assignment creator) can see submissions for assignments they created
        is_teacher = request.user.groups.filter(name="Teacher").exists()
        if is_teacher:
            return qs.filter(assigment__created_by=request.user)

        # ✅ Student (submitter) can see only their own submission
        is_student = request.user.groups.filter(name="Student").exists()
        if is_student:
            return qs.filter(submitted_by=request.user)

        # ❌ Others see nothing
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            # Set submitted_by to current user only on create
            obj.submitted_by = request.user

            # Prevent duplicate submissions
            if AssignmentSubmit.objects.filter(assigment=obj.assigment, submitted_by=request.user).exists():
                messages.error(request, "❌ You have already submitted this assignment.")
                return HttpResponseRedirect(request.path)  # ✅ prevent default success message
        
        super().save_model(request, obj, form, change)
    
@admin.register(Assignmentgrade)
class AssignmentgradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'assigment_submit', 'marks', 'due_date')
    search_fields = ('marks',)
    list_filter = ('due_date',)
    

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