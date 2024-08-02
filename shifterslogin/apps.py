from django.apps import AppConfig


class ShiftersloginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shifterslogin'

    def ready(self):
        import shifterslogin.signals #Import signals