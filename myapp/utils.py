from django.core.mail import send_mail
from django.conf import settings

def send_task_reminder_email(task):
    if task.user and task.user.email:
        subject = f"Reminder: Task '{task.title}' is due soon"
        message = f"Hello {task.user.username},\n\nThis is a reminder for your task:\n\nTitle: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}\n\nPlease make sure to complete it on time.\n\nBest regards,\nYour Task Manager"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [task.user.email])
