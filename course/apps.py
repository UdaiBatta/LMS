from django.apps import AppConfig


class CourseConfig(AppConfig):
    name = "course"

    def ready(self):
        from . import signals  # noqa: F401  (register signal handlers)
