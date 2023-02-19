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


class AlarmEntranceSettings(models.Model):
    ae_on = models.BooleanField(verbose_name='Сработка по датчику движения на входе включена', default=False)
    ae_token = models.CharField(max_length=100, verbose_name='токен для авторизации', blank=True, null=True)
    ae_addr = models.CharField(max_length=100, verbose_name='ip адрес wi-fi модуля', blank=True, null=True)
    on_at = models.DateTimeField(verbose_name='Дата и время включения режима', blank=True, null=True)
    off_at = models.DateTimeField(verbose_name='Дата и время выключения режима', blank=True, null=True)

    def __str__(self):
        return self.ae_token

    class Meta:
        verbose_name = 'Режим сработки у главного входа'
        verbose_name_plural = 'Режимы сработки у главного входа'
        ordering = ['-on_at']
