from rest_framework import serializers
from .models import (
    User, Admin, Student, Teacher, Department, Course, Exam, ExamSchedule,
    ExamResult, Attendance, Assignment, Payment, StudentCourseSchedule, CourseWork
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = '__all__'

class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class StudentCourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseSchedule
        fields = '__all__'

class CourseWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseWork
        fields = '__all__' 