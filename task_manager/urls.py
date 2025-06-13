from django.urls import include, path
from rest_framework.routers import DefaultRouter

from task_manager.views import (
    CommentViewSet,
    TaskFileViewSet,
    TaskViewSet,
    WorkspaceViewSet,
)


router = DefaultRouter()
router.register(r"workspaces", WorkspaceViewSet, basename="workspaces")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"files", TaskFileViewSet, basename="files")

urlpatterns = [
    path("", include(router.urls)),
]
