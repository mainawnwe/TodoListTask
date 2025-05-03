from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Task
from myapp.utils import send_task_reminder_email
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send email reminders for tasks with upcoming reminders'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        self.stdout.write(f"Current time: {now}")
        # Get all tasks with a reminder set
        all_reminder_tasks = Task.objects.filter(reminder__isnull=False, is_completed=False)
        self.stdout.write(f"Tasks with reminders: {all_reminder_tasks.count()}")
        for task in all_reminder_tasks:
            self.stdout.write(f"Task: {task.title}, Reminder: {task.reminder}")

        # Get tasks with reminder datetime within the last 10 minutes
        upcoming_reminders = Task.objects.filter(
            reminder__lte=now,
            reminder__gte=now - timezone.timedelta(minutes=10),
            is_completed=False
        )
        self.stdout.write(f"Tasks with upcoming reminders: {upcoming_reminders.count()}")

        for task in upcoming_reminders:
            try:
                send_task_reminder_email(task)
                self.stdout.write(self.style.SUCCESS(f"Sent reminder for task '{task.title}' to {task.user.email}"))
                logger.info(f"Sent reminder for task '{task.title}' to {task.user.email}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to send reminder for task '{task.title}': {e}"))
                logger.error(f"Failed to send reminder for task '{task.title}': {e}")
