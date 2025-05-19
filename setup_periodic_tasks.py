from celery import Celery
from celery.schedules import crontab

app = Celery('todo')

app.conf.beat_schedule = {
    'send-reminder-emails-every-10-minutes': {
        'task': 'myapp.tasks.send_reminder_emails',
        'schedule': crontab(minute='*/10'),
    },
}

app.conf.timezone = 'UTC'
