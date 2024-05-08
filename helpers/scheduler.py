from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import InactiveUser

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.db import transaction

def cleanup_inactive_users():
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    inactive_users = User.objects.filter(last_login__isnull=True, date_joined__lt=thirty_days_ago, is_active=False)
    with transaction.atomic():
        for user in inactive_users:
            if not InactiveUser.objects.filter(user=user).exists():
                InactiveUser.objects.create(
                    user=user,
                    username=user.username,
                    email=user.email,
                    date_joined=user.date_joined
                )

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        cleanup_inactive_users,
        trigger=CronTrigger(hour='*/23'),
        id="cleanup_inactive_users",
        max_instances=1,
        replace_existing=True,
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
