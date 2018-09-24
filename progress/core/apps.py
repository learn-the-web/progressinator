from django.apps import AppConfig


class ProgressCore(AppConfig):
    name = 'progress.core'
    label = 'progress_core'
    verbose_name = 'Progress Core'

    def ready(self):
        import progress.common.signals.common
