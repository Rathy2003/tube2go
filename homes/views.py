import os
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from homes.helper.helper import get_info, download_video, download_audio


@csrf_exempt
def download(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        format = request.POST.get('format')
        option = request.POST.get('option')
        filepath = ""
        if format == 'mp4':
            filename = download_video(url=url, target_resolution=option)
            filepath = f"{filename}"
        else:
            filename = download_audio(url=url, target_bitrate=option)
            filepath = f"{filename}"
        return JsonResponse({'status':'success','filepath':filepath})
    return  None

@csrf_exempt
def fetch_info(request):
    if request.method == "POST":
        url = request.POST.get('url')
        result = get_info(url)
        return JsonResponse(result)
    return None

@csrf_exempt
def delete_file(request):
    if request.method == "POST":
        filename = request.POST.get('filename')
        if filename:
            filepath = os.path.join(settings.MEDIA_ROOT, unquote(filename))
            if os.path.isfile(filepath):
                os.remove(filepath)
            return JsonResponse({'status':'success','message':'file deleted'})
    return None

def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render())

def download_file(request, filename):
    try:
        # Decode if your filename was URL-encoded
        safe_filename = unquote(filename)

        # Full path to the file
        file_path = os.path.join(settings.MEDIA_ROOT, safe_filename)

        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=safe_filename)
        else:
            raise Http404("File not found")
    except Exception as e:
        raise Http404("Error processing the download")

