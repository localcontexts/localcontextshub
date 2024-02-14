from django.apps import AppConfig
import sys

class HelpersConfig(AppConfig):
    name = 'helpers'

    def ready(self):
        if 'migrate' not in sys.argv:
            from helpers.scheduler import start_scheduler
            start_scheduler()