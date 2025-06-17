from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
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

    @action(detail=False, methods=["get"], url_path="by-date")
    def tasks_by_date(self, request):
        workspace_id = request.query_params.get("workspace_id")
        date_str = request.query_params.get("date")

        if not workspace_id or not date_str:
            return Response(
                {"detail": "workspace_id and date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_datetime = timezone.make_aware(
            datetime.combine(target_date, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(target_date, datetime.max.time())
        )

        tasks = Task.objects.filter(
            workspace__id=workspace_id,
            workspace__members=request.user,
            deadline__range=(start_datetime, end_datetime),
        )

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            task__workspace__members=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"], url_path="by-workspace")
    def comments_by_workspace(self, request):
        workspace_id = request.query_params.get("workspace_id")
        task_id = request.query_params.get("task_id")

        if not workspace_id:
            return Response(
                {"detail": "workspace_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            return Response(
                {"detail": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user not in workspace.members.all():
            return Response(
                {"detail": "You are not a member of this workspace."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comments = Comment.objects.filter(task__workspace=workspace)

        if task_id:
            comments = comments.filter(task_id=task_id)

        comments = comments.select_related("task", "author")
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


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
