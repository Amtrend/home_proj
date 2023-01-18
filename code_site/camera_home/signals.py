from django.db.models.signals import pre_delete
from .models import CameraEntranceSaveVideos
from django.dispatch.dispatcher import receiver


@receiver(pre_delete, sender=CameraEntranceSaveVideos)
def video_post_delete_handler(sender, **kwargs):
    video = kwargs["instance"]
    storage, path = video.video.storage, video.video.path
    storage.delete(path)
