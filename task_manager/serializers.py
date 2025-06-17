from django.contrib.auth import get_user_model
from rest_framework import serializers

from task_manager.models import Comment, Task, TaskFile, Workspace
from users.serializers import UserSerializer


User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.username", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "author_name", "text", "created_at", "task"]
        read_only_fields = ["author"]


class TaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFile
        fields = ["id", "file", "uploaded_at"]


class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    files = TaskFileSerializer(many=True, read_only=True)
    assignees = UserSerializer(many=True, read_only=True)
    assignee_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source="assignees",
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "workspace",
            "title",
            "description",
            "deadline",
            "priority",
            "status",
            "creator",
            "assignees",
            "assignee_ids",
            "created_at",
            "updated_at",
            "comments",
            "files",
        ]


class WorkspaceSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = ["id", "name", "creator", "members", "created_at"]
