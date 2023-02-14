from django.contrib import admin
from .models import *


@admin.register(CameraEntranceSaveVideos)
class CameraEntranceSaveVideosAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'video', 'start_recording', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('created_at',)
    fields = ('title', 'video', 'start_recording', 'created_at')
    list_per_page = 10


@admin.register(AlarmEntranceSettings)
class AlarmEntranceSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'ae_on', 'ae_token', 'on_at', 'off_at')
    list_display_links = ('id',)
    search_fields = ('ae_token',)
    fields = ('ae_on', 'ae_token', 'on_at', 'off_at')
    list_per_page = 10
