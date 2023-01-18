from django.apps import AppConfig


class CameraHomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'camera_home'

    def ready(self):
        import camera_home.signals
