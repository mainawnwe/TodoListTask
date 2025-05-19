from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Task
from myapp.utils import send_task_reminder_email

class Command(BaseCommand):
    help = 'Send reminder emails for tasks with upcoming reminders'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        upcoming_tasks = Task.objects.filter(reminder__lte=now, reminder__gte=now - timezone.timedelta(minutes=10), is_completed=False)
        for task in upcoming_tasks:
            send_task_reminder_email(task)
            self.stdout.write(f"Sent reminder for task: {task.title}")
