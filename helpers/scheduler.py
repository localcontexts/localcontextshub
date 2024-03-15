from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

def cleanup_inactive_users():
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    inactive_users = User.objects.filter(last_login__isnull=True, date_joined__lt=thirty_days_ago, is_active=False)
    inactive_users.delete()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        cleanup_inactive_users,
        trigger=CronTrigger(hour=0, minute=0),
        id="cleanup_inactive_users",
        max_instances=1,
        replace_existing=True,
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
