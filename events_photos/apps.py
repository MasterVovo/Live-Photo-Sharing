from django.apps import AppConfig

class EventsPhotosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events_photos'

    def ready(self):
        import events_photos.signals
