from flask import Flask, render_template, request, jsonify
import sys
import json
from werkzeug.datastructures import FileStorage
import os
from queue import Queue
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List
from threading import Thread
import subprocess


# Fix import path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from videoplayer import VideoPlayer


PROJECT_ROOT_PATH = Path(__file__).absolute().parent.parent
VIDEO_DIR = PROJECT_ROOT_PATH.joinpath('videos')


stdout_debug = Queue()


class Stdout:
    ''' Hijack stdout so we can debug print msgs. '''
    def __init__(self) -> None:
        self._out = sys.stdout
        sys.stdout = self

    def write(self, msg: str) -> None:
        stdout_debug.put(msg)
        self._out.write(msg)

    def flush(self) -> None:
        self._out.flush()

    def fileno(self) -> int:
        return self._out.fileno()


app = Flask(__name__, template_folder='.')
stdout = Stdout()

import logging
logging.getLogger("werkzeug").disabled = True


@dataclass
class Video:
    name: str
    fps: int
    abs_path: str
    image_path: str
    audio_path: str


def convert_video(video_path: str, image_path: str, audio_path: str, fps: int) -> None:
    cmd = f'ffmpeg -i {video_path} -r {fps} -f image2 {image_path}/image-%4d.jpg'
    print('Converting video to images using ffmpeg...')
    subprocess.Popen(cmd.split(' '), stdout=stdout, stderr=stdout)
    print('Video conversion complete!')

    print('Extracting audio...')
    cmd = f'ffmpeg -i {video_path} -q:a 0 -map a {audio_path}'
    subprocess.Popen(cmd.split(' '), stdout=stdout, stderr=stdout)
    print('Audio extraction complete!')



class VideoDirectory:

    @staticmethod   
    def get_videos() -> List[Video]:
        videos = []
        for video in os.listdir(VIDEO_DIR):
            fps = int(video.split('_')[-1].strip())
            abs_path = VIDEO_DIR.joinpath(video)
            image_path = abs_path.joinpath('images')
            audio_path = abs_path.joinpath('audio.wav')

            videos.append(Video(
                video,
                fps,
                abs_path,
                image_path,
                audio_path if audio_path.exists() else None
            ))

        return videos

    @classmethod
    def get_video(cls, video_name: str) -> Video:
        videos = cls.get_videos()
        for video in videos:
            if video.name == video_name:
                return video

    def video_exists(self, video_name: str) -> bool:
        videos = self.get_videos()
        for video in videos:
            if video.name == video_name:
                return True
        return False

    def add_video(self, video: FileStorage, fps: int) -> None:
        filename = video.filename.split('.')[0]
        dirname = f'{filename}_{fps}'
        # Directory for video project
        dirpath = VIDEO_DIR.joinpath(dirname)

        image_path = dirpath.joinpath('images')
        audio_path = dirpath.joinpath('audio.wav')

        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
            os.mkdir(image_path)

        # Video file path
        filepath = dirpath.joinpath(video.filename)
        print(f'Saving video {video.filename} to {filepath}')
        video.save(filepath)

        print('Converting video with ffmpeg')
        Thread(target=convert_video, args=(filepath, image_path, audio_path, fps)).start()



video_dir = VideoDirectory()
video_player: VideoPlayer = None


# -- WEB -- #

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        # Save video
        video_file = request.files.get('video')
        fps = request.form.get('fps', 30)
        video_dir.add_video(video_file, fps)

    return render_template(
        'index.html',
        videos=video_dir.get_videos()
    )


@app.route('/play', methods=['POST'])
def play():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    video = data.get('video')

    video = video_dir.get_video(video)

    print(f'Playing {video.name}')
    global video_player
    video_player = VideoPlayer(video.fps, video.image_path, video.audio_path)

    Thread(target=video_player.start).start()

    return ('', 204)


@app.route('/stop', methods=['POST'])
def stop():
    print(f'Stopping video!')
    global video_player
    if video_player is not None:
        def _stop():
            global video_player
            video_player.stop()

        Thread(target=_stop).start()

    return ('', 204)


@dataclass
class Status:
    type: str
    msg: str

@app.route('/status')
def status():
    if stdout_debug.empty():
        status = Status(
            'status',
            ''
        )
    else:
        status = Status(
            'status',
            stdout_debug.get()
        )
    return jsonify(asdict(status))