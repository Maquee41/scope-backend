from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import get_user_profile_by_id, profile_details, register


urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", profile_details, name="profile_details"),
    path("register/", register, name="register"),
    path(
        "profile/<int:user_id>/",
        get_user_profile_by_id,
        name="user-profile-by-id",
    ),
]
