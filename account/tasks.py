from celery import shared_task
from datetime import date, datetime
from .models import MyUser, Preference, Task
from mandrill import Mandrill

@shared_task
def create_tasks_based_on_preferences():
    preferences = Preference.objects.all()
    for preference in preferences:
        today = date.today()
        preferred_days = preference.preferred_days.split(',')  # Split preferred days string
        if today.strftime('%A') in preferred_days:  # Check if today is a preferred day
            preferred_time = datetime.combine(today, preference.preferred_time)
            # Check if a task with the same title and due date already exists for the user
            existing_task = Task.objects.filter(title=f"{preference.name} task", due_at=preferred_time, user=preference.user).exists()
            if not existing_task and preferred_time > datetime.now():
                task = Task.objects.create(
                    title=f"{preference.name} task",
                    description=f"Automatically created task based on user preference for {preference.name}",
                    due_at=preferred_time,
                    user=preference.user
                )
                task.save()

@shared_task
def send_task_reminders():
    # Initialize Mandrill client
    mandrill_client = Mandrill('feczsxGoFPR7Kc1Wqdd841Vw')

    preferences = Preference.objects.all()
    for preference in preferences:
        today = datetime.now().date()
        tasks_due_today = Task.objects.filter(due_at__date=today, user=preference.user)

        # Send reminders for each task
        for task in tasks_due_today:
            reminder_message = f"Don't forget to complete the task: {task.title}"
            message = {
                'from_email': 'amanb1145@gmail.com',
                'to': [{'email': preference.user.email}],
                'subject': 'Task Reminder',
                'text': reminder_message
            }

            try:
                result = mandrill_client.messages.send(message=message)
                print(result)
            except Exception as e:
                print(f"Error sending reminder email to {preference.user.email}: {e}")
