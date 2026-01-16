from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('launch/', views.launch_view, name='launch'),
    path('launch/companies/', views.launch_companies_view, name='launch_companies'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact_view, name='contact'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
]
