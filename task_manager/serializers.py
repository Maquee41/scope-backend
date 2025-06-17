from django.contrib.auth import get_user_model
from rest_framework import serializers

from task_manager.models import Comment, Task, TaskFile, Workspace
from users.serializers import UserSerializer


User = get_user_model()


class TaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFile
        fields = ["id", "file", "uploaded_at"]


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(
        source="author.username", read_only=True
    )
    files = TaskFileSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "author_name",
            "text",
            "created_at",
            "task",
            "files",
            "uploaded_files",
        ]
        read_only_fields = ["author"]

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])
        comment = Comment.objects.create(**validated_data)

        for file in uploaded_files:
            task_file = TaskFile.objects.create(file=file, task=comment.task)
            comment.files.add(task_file)

        return comment


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
