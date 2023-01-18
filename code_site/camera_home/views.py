from django.shortcuts import render, get_object_or_404
from django.http.response import StreamingHttpResponse, JsonResponse, FileResponse
from .models import *
from .services import open_file
from django.contrib.auth import authenticate, login
from .forms import *
from django.contrib.auth.decorators import login_required


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
    import datetime as dt
    cur_dt = dt.datetime.now()
    ce_videos = CameraEntranceSaveVideos.objects.all()
    response_data = {
        "ce_videos": ce_videos,
        "cur_dt": cur_dt,
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
    response_data = {

    }
    return render(request, 'camera_home/settings.html', response_data)
