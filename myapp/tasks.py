from celery import shared_task
from django.utils import timezone
from myapp.models import Task
from myapp.utils import send_task_reminder_email

@shared_task
def send_reminder_emails():
    now = timezone.now()
    upcoming_tasks = Task.objects.filter(reminder__lte=now, reminder__gte=now - timezone.timedelta(minutes=10), is_completed=False)
    for task in upcoming_tasks:
        send_task_reminder_email(task)
