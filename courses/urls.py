from django.urls import path

app_name = 'courses'

from .views import course_list_view, enroll_course_view, drop_course_view, student_schedule_view, student_grades_view, student_assignment_list_view, student_exam_list_view, student_payments_view, teacher_course_list_view, create_assignment_view, teacher_assignment_list_view, teacher_submission_list_view, grade_submission_view, teacher_enrolled_students_view, teacher_session_list_view, mark_attendance_view, teacher_attendance_history_view, teacher_exam_list_view, teacher_exam_students_list_view, grade_exam_view, create_exam_view, edit_exam_view, delete_exam_view, teacher_all_assignments_view, teacher_all_attendance_view, teacher_all_exams_view, teacher_all_grades_view, teacher_course_material_list_view, teacher_upload_course_material_view

urlpatterns = [
    path('list/', course_list_view, name='course_list'), # URL for listing all courses
    path('enroll/<int:course_id>/', enroll_course_view, name='enroll_course'), # URL for enrolling in a course
    path('drop/<int:course_id>/', drop_course_view, name='drop_course'),   # URL for dropping a course
    path('schedule/', student_schedule_view, name='schedule'),         # URL for student schedule
    path('grades/', student_grades_view, name='grades'),           # URL for student grades
    path('assignments/', student_assignment_list_view, name='assignments'), # URL for student assignments
    path('exams/', student_exam_list_view, name='exams'),           # URL for student exams
    path('payments/', student_payments_view, name='payments'),         # URL for student payments

    # Teacher URLs
    path('teacher/courses/', teacher_course_list_view, name='teacher_course_list'), # URL for listing teacher's courses
    path('teacher/assignments/all/', teacher_all_assignments_view, name='teacher_all_assignments'),
    path('teacher/attendance/all/', teacher_all_attendance_view, name='teacher_all_attendance'),
    path('teacher/exams/all/', teacher_all_exams_view, name='teacher_all_exams'),
    path('teacher/grades/all/', teacher_all_grades_view, name='teacher_all_grades'),
    path('teacher/courses/<int:course_id>/assignments/create/', create_assignment_view, name='create_assignment'), # URL for creating assignment
    path('teacher/courses/<int:course_id>/assignments/', teacher_assignment_list_view, name='teacher_assignment_list'), # URL for listing assignments for a teacher's course
    path('teacher/submissions/<int:assignment_id>/', teacher_submission_list_view, name='teacher_submission_list'), # URL for listing submissions for an assignment
    path('teacher/submissions/grade/<int:submission_id>/', grade_submission_view, name='grade_submission'), # URL for grading a submission
    path('teacher/courses/<int:course_id>/students/', teacher_enrolled_students_view, name='teacher_enrolled_students'), # URL for listing students in a teacher's course
    path('teacher/courses/<int:course_id>/sessions/', teacher_session_list_view, name='teacher_session_list'), # URL for listing sessions for a course
    path('teacher/sessions/<int:session_id>/attendance/', mark_attendance_view, name='mark_attendance'), # URL for marking attendance for a session
    path('teacher/courses/<int:course_id>/attendance/history/', teacher_attendance_history_view, name='teacher_attendance_history'), # URL for attendance history
    path('teacher/courses/<int:course_id>/exams/', teacher_exam_list_view, name='teacher_exam_list'), # URL for listing exams for a course
    path('teacher/courses/<int:course_id>/exams/create/', create_exam_view, name='create_exam'), # URL for creating a new exam
    path('teacher/exams/<int:exam_id>/edit/', edit_exam_view, name='edit_exam'), # URL for editing an exam
    path('teacher/exams/<int:exam_id>/delete/', delete_exam_view, name='delete_exam'), # URL for deleting an exam
    path('teacher/exams/<int:exam_id>/students/', teacher_exam_students_list_view, name='teacher_exam_students_list'),
    path('teacher/exams/<int:exam_id>/students/<int:student_id>/grade/', grade_exam_view, name='grade_exam'),
    # URLs for Course Materials
    path('teacher/courses/<int:course_id>/materials/', teacher_course_material_list_view, name='teacher_course_material_list'),
    path('teacher/courses/<int:course_id>/materials/upload/', teacher_upload_course_material_view, name='teacher_upload_course_material'),
]