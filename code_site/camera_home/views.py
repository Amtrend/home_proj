from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import StreamingHttpResponse, JsonResponse, FileResponse
from .models import *
from .services import open_file
from django.contrib.auth import authenticate, login
from .forms import *
from .tasks import *
from django.contrib.auth.decorators import login_required
from datetime import datetime as dt
from celery.contrib.abortable import AbortableAsyncResult


@login_required
def streaming_video(request, pk):
    file, status_code, content_length, content_range = open_file(request, pk)
    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range
    return response


@login_required
def download_video(request, pk):
    obj = get_object_or_404(CameraEntranceSaveVideos, id=pk)
    filename = obj.video.path
    response = FileResponse(open(filename, 'rb'))
    return response


@login_required
def main_page(request):
    return render(request, 'camera_home/index.html')


def login_page(request):
    form = LoginForm()
    if request.method == 'POST':
        if 'login_form_sbmt' in request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user = authenticate(username=cd['username'], password=cd['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return JsonResponse({'answer': 'ok'}, status=200)
                    else:
                        return JsonResponse({'answer': 'пользователь не активирован'}, status=401)
                else:
                    return JsonResponse({'answer': 'логин или пароль не верные'}, status=403)
            else:
                return JsonResponse({'answer': 'логин или пароль не верные'}, status=403)
    response_data = {
        'form': form,
    }
    return render(request, 'camera_home/login.html', response_data)


@login_required
def livecams_feed_page(request):
    return render(request, 'camera_home/livecams_feed.html')


@login_required
def cams_archive_page(request):
    ce_videos = CameraEntranceSaveVideos.objects.all()
    response_data = {
        "ce_videos": ce_videos,
    }
    if request.method == 'POST':
        if 'del_video_aus_yes' in request.POST:
            target_video_id = request.POST.get("del_video_aus_yes")
            target_video = CameraEntranceSaveVideos.objects.get(id=target_video_id)
            target_video.delete()
            return JsonResponse({'answer': target_video_id}, status=200)
    return render(request, 'camera_home/cams_archive.html', response_data)


@login_required
def settings_page(request):
    ae_settings = AlarmEntranceSettings.objects.first()
    response_data = {
        'ae_settings': ae_settings,
    }
    if 'settings_save' in request.POST:
        ae_on_change = request.POST.get('set_alarm_on_entrance')
        if ae_settings.ae_on:
            if not ae_on_change:
                ae_settings.ae_on = False
                ae_settings.off_at = dt.now()
                ae_settings.save()
                cur_ae_task_id = ae_settings.ae_task_id
                revoked = AbortableAsyncResult(cur_ae_task_id)
                revoked.abort()
        else:
            if ae_on_change:
                new_ae_task = go_alarm_entrance_task.delay()
                ae_settings.ae_task_id = new_ae_task.id
                ae_settings.ae_on = True
                ae_settings.on_at = dt.now()
                ae_settings.off_at = None
                ae_settings.save()
            else:
                ae_settings.off_at = dt.now()
                ae_settings.save()
                cur_ae_task_id = ae_settings.ae_task_id
                revoked = AbortableAsyncResult(cur_ae_task_id)
                revoked.abort()
        return redirect('home')
    return render(request, 'camera_home/settings.html', response_data)
