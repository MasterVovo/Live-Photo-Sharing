import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Photo

@receiver(post_delete, sender=Photo)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
