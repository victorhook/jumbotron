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
import logging

# Fix import path
sys.path.append(str(Path(__file__).absolute().parent.parent.joinpath('src')))
from client import Client


PROJECT_ROOT_PATH = Path(__file__).absolute().parent.parent
VIDEO_DIR = PROJECT_ROOT_PATH.joinpath('videos')

stdout_debug = Queue()


class Stdout(logging.StreamHandler):
    ''' Hijack stdout so we can debug print msgs. '''
    def __init__(self) -> None:
        super().__init__()
        self._out = sys.stdout
        sys.stdout = self
        self.formatter = logging.Formatter('[%(name)s::%(levelname)s] %(message)s\n')

    def emit(self, record) -> None:
        text = self.formatter.format(record)
        self.write(text)

    def write(self, msg: str) -> None:
        stdout_debug.put(msg)
        self._out.write(msg)

    def flush(self) -> None:
        self._out.flush()

    def fileno(self) -> int:
        return self._out.fileno()

stdout = Stdout()
logging.basicConfig(level=logging.DEBUG, handlers=[stdout])
logging.getLogger("werkzeug").disabled = True
logger = logging.getLogger(__name__)

@dataclass
class Video:
    name: str
    fps: int
    abs_path: str
    image_path: str
    audio_path: str


@dataclass
class Status:
    type: str
    msg: str


def convert_video(video_path: str, image_path: str, audio_path: str, fps: int) -> None:
    cmd = f'ffmpeg -i {video_path} -r {fps} -f image2 {image_path}/image-%4d.jpg'
    logger.info('Converting video to images using ffmpeg...')
    subprocess.Popen(cmd.split(' '), stdout=stdout, stderr=stdout)
    logger.info('Video conversion complete!')

    logger.info('Extracting audio...')
    cmd = f'ffmpeg -i {video_path} -q:a 0 -map a {audio_path}'
    subprocess.Popen(cmd.split(' '), stdout=stdout, stderr=stdout)
    logger.info('Audio extraction complete!')


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
        logger.info(f'Saving video {video.filename} to {filepath}')
        video.save(filepath)

        logger.info('Converting video with ffmpeg')
        Thread(target=convert_video, args=(filepath, image_path, audio_path, fps)).start()


video_dir = VideoDirectory()
client = Client()
app = Flask(__name__, template_folder='.')


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

    logger.info(f'Playing {video.name}')
    client.play_video(video.image_path, video.fps, video.audio_path)

    return ('', 204)


@app.route('/stop', methods=['POST'])
def stop():
    logger.info(f'Stopping video!')
    client.stop_video()
    return ('', 204)


@app.route('/set_color', methods=['POST'])
def set_color():
    color = request.form.get('color')
    logger.info(f'Setting color: {color}')
    client.set_led(color)
    return ('', 204)


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
