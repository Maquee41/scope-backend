from django.contrib.auth import get_user_model
from rest_framework import serializers

from task_manager.models import Comment, Task, TaskFile, Workspace


User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Workspace
        fields = ["id", "name", "creator", "members", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.username", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "author", "author_name", "text", "created_at"]


class TaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFile
        fields = ["id", "file", "uploaded_at"]


class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    files = TaskFileSerializer(many=True, read_only=True)

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
            "created_at",
            "updated_at",
            "comments",
            "files",
        ]
