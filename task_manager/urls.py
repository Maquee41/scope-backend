from django.urls import include, path
from rest_framework.routers import DefaultRouter

from task_manager.views import (
    CommentViewSet,
    NotificationViewSet,
    TaskFileViewSet,
    TaskViewSet,
    WorkspaceViewSet,
    get_workspace_details,
)


router = DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet, basename="workspaces")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"files", TaskFileViewSet, basename="files")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "workspace/<int:workspace_id>/",
        get_workspace_details,
        name="workspace-details",
    ),
]
