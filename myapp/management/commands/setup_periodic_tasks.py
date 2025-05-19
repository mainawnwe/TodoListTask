from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Setup periodic tasks for Celery Beat'

    def handle(self, *args, **kwargs):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )
        PeriodicTask.objects.update_or_create(
            name='Send Task Reminders',
            defaults={
                'interval': schedule,
                'task': 'myapp.tasks.send_reminders_task',
            }
        )
        self.stdout.write(self.style.SUCCESS('Periodic task registered successfully.'))
