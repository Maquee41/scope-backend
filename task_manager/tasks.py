import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from task_manager.models import Notification, Task


logger = logging.getLogger(__name__)


@shared_task
def notify_upcoming_deadlines():
    logger.info("🚀 notify_upcoming_deadlines started")

    now = timezone.now()
    soon = now + timedelta(days=1)

    tasks = (
        Task.objects.filter(
            deadline__isnull=False,
            deadline__gte=now,
            deadline__lte=soon,
            status__in=["todo", "in_progress"],
        )
        .select_related("workspace", "creator")
        .prefetch_related("assignees")
    )

    for task in tasks:
        if not task.workspace:
            logger.warning(f"⚠️ Task {task.id} has no workspace assigned")
            continue

        try:
            deadline_local = timezone.localtime(task.deadline).strftime(
                "%b %d, %Y at %I:%M %p"
            )
            workspace_name = task.workspace.name
            message = f"Task '{task.title}' is due soon on {deadline_local} (Workspace: {workspace_name})"

            if task.creator:
                if not Notification.objects.filter(
                    user=task.creator, task=task
                ).exists():
                    Notification.objects.create(
                        user=task.creator,
                        message=message,
                        task=task,
                    )
                    logger.info(
                        f"✅ Notification created for creator {task.creator.id}"
                    )

            for assignee in task.assignees.exclude(
                id=task.creator.id if task.creator else None
            ):
                if not Notification.objects.filter(
                    user=assignee, task=task
                ).exists():
                    Notification.objects.create(
                        user=assignee,
                        message=message,
                        task=task,
                    )
                    logger.info(
                        f"✅ Notification created for assignee {assignee.id}"
                    )

        except Exception as e:
            logger.error(f"❌ Error processing task {task.id}: {str(e)}")
            continue
