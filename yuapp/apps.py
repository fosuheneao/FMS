from django.apps import AppConfig


class YuappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yuapp'

    def ready(self):
        import yuapp.signals  # noqa