from django.contrib import admin
from .models import *


@admin.register(CameraEntranceSaveVideos)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'video', 'start_recording', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('created_at',)
    fields = ('title', 'video', 'start_recording', 'created_at')
    list_per_page = 10
