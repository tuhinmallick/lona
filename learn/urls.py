from django.urls import path
from . import views

urlpatterns = [
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/select-teacher/', views.select_teacher, name='select_teacher'),
    path('student/learning-session/', views.learning_session, name='learning_session'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/curriculum-upload/', views.curriculum_upload, name='curriculum_upload'),
    path('teacher/voice-recording/', views.voice_recording, name='voice_recording'),
]