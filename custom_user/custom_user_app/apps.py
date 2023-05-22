from django.apps import AppConfig


class CustomUserAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_user_app'

    def ready(self):
        import custom_user_app.signals
