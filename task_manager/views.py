from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from task_manager.models import Comment, Task, TaskFile, Workspace
from task_manager.permissions import IsWorkspaceMember
from task_manager.serializers import (
    CommentSerializer,
    TaskFileSerializer,
    TaskSerializer,
    WorkspaceSerializer,
)


User = get_user_model()


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.save()
        workspace.members.add(self.request.user)

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        workspace = self.get_object()
        username = request.data.get("username")

        if not username:
            return Response(
                {"detail": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if user in workspace.members.all():
            return Response(
                {"detail": "User is already a member"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workspace.members.add(user)
        return Response(
            {"detail": f"User {username} added to workspace"},
            status=status.HTTP_200_OK,
        )


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        queryset = Task.objects.filter(workspace__members=self.request.user)
        workflow_id = self.request.query_params.get("workflow_id")
        if workflow_id is not None:
            queryset = queryset.filter(workspace=workflow_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            task__workspace__members=self.request.user
        )


class TaskFileViewSet(viewsets.ModelViewSet):
    serializer_class = TaskFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskFile.objects.filter(
            task__workspace__members=self.request.user
        )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_workspace_details(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    if request.user != workspace.creator:
        return Response(
            {"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN
        )

    serializer = WorkspaceSerializer(workspace)
    return Response(serializer.data)
