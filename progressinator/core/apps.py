from django.apps import AppConfig


class ProgressinatorCore(AppConfig):
    name = 'progressinator.core'
    label = 'progress_core'
    verbose_name = 'Progressinator Core'

    def ready(self):
        import progressinator.common.signals.common
        import progressinator.common.signals.user

