from django.apps import AppConfig


class HelpersConfig(AppConfig):
    name = 'helpers'

    def ready(self):
        from helpers.scheduler import start_scheduler
        start_scheduler()