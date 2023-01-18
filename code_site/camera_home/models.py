from django.db import models


class CameraEntranceSaveVideos(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название файла')
    video = models.FileField(upload_to='archive/cam_entrance/', verbose_name='Путь к файлу')
    start_recording = models.DateTimeField(verbose_name='Дата и время начала записи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время сохранения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Видео с камеры у входа'
        verbose_name_plural = 'Видео с камеры у входа'
        ordering = ['-created_at']
