from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuthAPI.settings')

app = Celery('account')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Schedule tasks to run every 5 minutes
app.conf.beat_schedule = {
    'create-tasks-every-5-minutes': {
        'task': 'account.tasks.create_tasks_based_on_preferences',
        'schedule': 300,  # 5 minutes in seconds
    },
    'send-reminders-every-5-minutes': {
        'task': 'account.tasks.send_task_reminders',
        'schedule': 300,  # 5 minutes in seconds
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
