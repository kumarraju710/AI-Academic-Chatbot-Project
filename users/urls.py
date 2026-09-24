from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('student-login/', views.student_login, name='student_login'),
    path('student-register/', views.student_register, name='student_register'),

    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-register/', views.admin_register, name='admin_register'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('analytics/', views.analytics, name='analytics'),

    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),

    path('logout/', views.user_logout, name='logout'),
]
