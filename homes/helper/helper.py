import os
import re

import unicodedata
import yt_dlp
from pathvalidate import sanitize_filename


def safe_filename(name):
    # Normalize Unicode characters
    name = unicodedata.normalize('NFKD', name)

    # Remove filesystem-unsafe characters but keep Khmer/Unicode letters
    name = re.sub(r'[\\/*?:"<>|]', '', name)

    # Optional: trim long titles
    return name[:150].strip()

def get_video_resolution(url):
    ytdl_opts = {
        'quiet':True,
        'format':'bestvideo',
    }
    resolutions = []
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        for f in info['formats']:
            if 'height' in f and f['height'] is not None:
                resolution = f"{f['height']}p"
                if resolution not in resolutions and len(resolution) > 3:
                    resolutions.append(resolution)
        sorted_resolutions = sorted(resolutions, key=lambda x: int(x[:-1]), reverse=True)
    return sorted_resolutions

def get_info(url):
    result = {}
    resolutions = []
    bitrates = []
    ytdl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        # resolution
        for f in info['formats']:
            if 'height' in f and f['height'] is not None:
                resolution = f"{f['height']}p"
                if resolution not in resolutions and len(resolution) > 3:
                    resolutions.append(resolution)
        sorted_resolutions = sorted(resolutions, key=lambda x: int(x[:-1]), reverse=True)
        result["mp4"] = sorted_resolutions

        # audio bit rate
        for fmt in info['formats']:
            if fmt.get('abr'):
                bitrate = int(fmt['abr'])
                if bitrate not in bitrates:
                    bitrates.append(f"{bitrate}kbps")
        sorted_audio_bitrates = sorted(bitrates, key=lambda x: int(x[:-4]), reverse=True)

        result["mp3"] = sorted_audio_bitrates

        # title, duration and thumbnail

        result["title"] = info.get("title")
        result["duration"] =  info.get("duration")
        result["thumbnail"] = info.get("thumbnail")

        return result

def fetch_audio_birate(url):
    ydl_opts = {
        'format':'bestaudio'
    }
    bitrates = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        for fmt in info['formats']:
            if fmt.get('abr'):
                bitrate = int(fmt['abr'])
                if bitrate not in bitrates:
                    bitrates.append(f"{bitrate}kbps")
        sorted_audio_bitrates = sorted(bitrates, key=lambda x: int(x[:-4]), reverse=True)
    return sorted_audio_bitrates

def get_ffmpeg_path():
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg')
    return os.path.join(base_path,'bin', 'ffmpeg.exe')


def download_video(url, target_resolution):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        safe_title = safe_filename(title)

    yt_dlp_opts = {
        'format': f'bestvideo[height={target_resolution[:-1]}]+bestaudio[ext=m4a]/best[height={target_resolution[:-1]}]',
        'quiet': True,
        'merge_output_format': 'mp4',
        'ffmpeg_location': get_ffmpeg_path(),
        'outtmpl': os.path.join("media", f'{safe_title}.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
        ydl.download([url])

    return f"{safe_title}.mp4"


def download_audio(url, target_bitrate):
    target_bitrate = target_bitrate[:-4]  # remove "kbps"

    # Step 1: Get video info and sanitize title
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        safe_title = sanitize_filename(title)

    # Step 2: Set download options
    ydl_opts = {
        'format': f'bestaudio[abr<={target_bitrate}]',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(target_bitrate)
            }
        ],
        'ffmpeg_location': get_ffmpeg_path(),
        'outtmpl': os.path.join('media', f'{safe_title}.%(ext)s'),
        'quiet': True
    }

    # Step 3: Download audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Step 4: Return the filename for frontend use
    return f"{safe_title}.mp3"




