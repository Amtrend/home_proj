import os

from datetime import datetime as dt
from pathlib import Path

from .forms import *
from .models import *
from .services import open_file
from .tasks import *

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import StreamingHttpResponse, JsonResponse, FileResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from smart_home.settings import STUN_DOMAIN, RTCUSER, RTCPASS, MEDIA_ROOT


@login_required
def streaming_video(request, cam, pk):
    file, status_code, content_length, content_range = open_file(request, cam, pk)
    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range
    return response


@login_required
def download_video(request, cam, pk):
    if cam == 'entry':
        obj = get_object_or_404(CameraEntranceSaveVideos, id=pk)
    if cam == 'b_entry':
        obj = get_object_or_404(CameraBEntranceSaveVideos, id=pk)
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
    # ce_videos = CameraEntranceSaveVideos.objects.all()
    # response_data = {
    #     "ce_videos": ce_videos,
    # }
    # if request.method == 'POST':
    #     if 'del_video_aus_yes' in request.POST:
    #         target_video_id = request.POST.get("del_video_aus_yes")
    #         target_video = CameraEntranceSaveVideos.objects.get(id=target_video_id)
    #         target_video.delete()
    #         return JsonResponse({'answer': target_video_id}, status=200)
    # return render(request, 'camera_home/cams_archive.html', response_data)
    return render(request, 'camera_home/cams_archive.html')


@login_required
def cam_archive_page(request, cam):
    if cam == 'entry':
        ce_videos = CameraEntranceSaveVideos.objects.all()
        p_title = "Архив камеры у главного входа"
    if cam == 'b_entry':
        ce_videos = CameraBEntranceSaveVideos.objects.all()
        p_title = "Архив камеры у входа на заднем дворе"
    response_data = {
        "ce_videos": ce_videos,
        "p_title": p_title,
        "cam": cam,
    }
    if request.method == 'POST':
        if 'del_video_aus_yes' in request.POST:
            target_video_id = request.POST.get("del_video_aus_yes")
            if cam == 'entry':
                target_video = CameraEntranceSaveVideos.objects.get(id=target_video_id)
            if cam == 'b_entry':
                target_video = CameraBEntranceSaveVideos.objects.get(id=target_video_id)
            target_video.delete()
            return JsonResponse({'answer': target_video_id}, status=200)
    return render(request, 'camera_home/cam_archive.html', response_data)


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
        else:
            if ae_on_change:
                if not ae_settings.ae_token:
                    ae_settings.ae_token = os.environ.get("AES_TOKEN")
                ae_settings.ae_on = True
                ae_settings.on_at = dt.now()
                ae_settings.off_at = None
                ae_settings.save()
        return redirect('home')
    # if 'settings_sens_rest' in request.POST:
    #     print(request.POST)
    #     return redirect('home')
    #     # return render(request, 'camera_home/settings.html', response_data)
    return render(request, 'camera_home/settings.html', response_data)


@csrf_exempt
def sensors_resp_page(request):
    if request.method == 'POST':
        # print(request.POST)
        place = request.POST.get('place')
        if place:
            if place == 'entrance':
                s_type = request.POST.get('type')
                token = request.POST.get('token')
                # ip_addr = request.POST.get('ipaddr')
                cur_sens_set = AlarmEntranceSettings.objects.first()
                # if ip_addr:
                #     cur_sens_set.ae_addr = ip_addr
                #     cur_sens_set.save()
                # else:
                cur_sens_token = cur_sens_set.ae_token
                if cur_sens_set.ae_on:
                    if s_type == 'pir' and token == cur_sens_token:
                        cur_dt = dt.now().strftime("%H:%M:%S %d.%m.%Y")
                        go_alarm_entrance_task.delay(targ_timesamp=cur_dt)
    return JsonResponse({'answer': 'ok'}, status=200)


def auth_check_webrtc(request):
    if request.user.is_authenticated:
        return HttpResponse("OK", status=200)
    return HttpResponse("Unauthorized", status=401)


@login_required
def get_webrtc_config(request):
    return JsonResponse({
        "iceServers": [
            {"urls": f"stun:{STUN_DOMAIN}:3478"},
            {
                "urls": f"turn:{STUN_DOMAIN}:3478",
                "username": RTCUSER,
                "credential": RTCPASS
            }
        ]
    })

@login_required
def show_archive_video(request, cam, pk):
    if cam == 'entry':
        _video = get_object_or_404(CameraEntranceSaveVideos, pk=pk)
    elif cam == 'b_entry':
        _video = get_object_or_404(CameraBEntranceSaveVideos, pk=pk)
    else:
        raise Http404()

    if not _video or not _video.video:
        raise Http404()

    file_path = Path(_video.video.path)
    if not file_path.exists():
        raise Http404()

    relative_path = file_path.relative_to(MEDIA_ROOT)
    response = HttpResponse()
    response['Content-Type'] = 'video/mp4'
    response['X-Accel-Redirect'] = f'/protected_media/{relative_path}'
    return response
