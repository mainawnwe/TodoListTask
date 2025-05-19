from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_task_reminder_email(task):
    subject = f"Reminder: Task '{task.title}' is due soon"
    message = f"Hello {task.user.username},\n\nThis is a reminder that your task '{task.title}' is due on {task.due_date}.\n\nDescription:\n{task.description}\n\nPlease make sure to complete it on time.\n\nBest regards,\nYour ToDo App"
    recipient_list = [task.user.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    # Send real-time notification via WebSocket
    channel_layer = get_channel_layer()
    group_name = f'user_{task.user.id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'message': f"Reminder: Task '{task.title}' is due soon!"
        }
    )
