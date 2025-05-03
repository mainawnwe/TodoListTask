from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Task
from myapp.utils import send_task_reminder_email
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send reminder emails for tasks with upcoming reminders'

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_window_start = now
        reminder_window_end = now + timedelta(hours=1)

        tasks_to_remind = Task.objects.filter(
            reminder__gte=reminder_window_start,
            reminder__lte=reminder_window_end,
            is_completed=False
        )

        for task in tasks_to_remind:
            send_task_reminder_email(task)
            self.stdout.write(self.style.SUCCESS(f'Reminder sent for task: {task.title}'))
