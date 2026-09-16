from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [

    # Authentication
    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    # Email OTP
    path(
        'verify-otp/',
        views.verify_otp_view,
        name='verify_otp'
    ),

    path(
        'resend-otp/',
        views.resend_otp_view,
        name='resend_otp'
    ),

    # Profile Settings
    path(
        'settings/',
        views.profile_settings_view,
        name='settings'
    ),

    # Theme API
    path(
        'api/theme/',
        views.toggle_theme,
        name='toggle_theme'
    ),

]