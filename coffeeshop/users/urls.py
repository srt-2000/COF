from __future__ import annotations

from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordChangeView
from django.urls import path
from users import views

# Authentication URL patterns
urlpatterns = [
    # Login page
    path("login/", views.LoginUser.as_view(), name="login"),
    # Logout page
    path("logout/", LogoutView.as_view(), name="logout"),
    # User registration
    path("registration/", views.RegisterUser.as_view(), name="registration"),
    # User profile
    path("profile/", views.ProfileUser.as_view(), name="profile"),
    # Password change
    path("password-change/", PasswordChangeView.as_view(), name="password_change"),
    # Password change confirmation
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(template_name="password_change_done.html"),
        name="password_change_done",
    ),
]
