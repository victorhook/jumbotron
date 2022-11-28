import socket
import sys
from typing import List
from videoplayer import VideoPlayer
import time
from threading import Thread


IP   = '0.0.0.0'
PORT = 9999

DEFAULT_IMAGE_DIR = '.'


class Command:
    # PLAY fps=10 image_dir=dsadas audio=kakak
    PLAY_VIDEO = 'PLAY'
    STOP_VIDEO = 'STOP'



class VideoPlayerServer:

    def __init__(self) -> None:
        self._sock: socket.socket = None
        self._video_player: VideoPlayer = None

    def start(self, ip: str, port: int) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((ip, port))
        self._sock.listen()
        print(f'Video server started at {ip}:{port}')

        while True:
            print('Waiting for new client...')
            con, addr = self._sock.accept()
            print(f'New connection from {addr}')
            self._handle_connection(con, addr)

    def _handle_connection(self, con: socket.socket, addr) -> None:
        con.setblocking(True)
        connected = True
        while connected:
            msg = con.recv(1024)

            if not msg:
                connected = False
                continue

            msg = msg.decode('utf-8')
            print(f'RX: {msg}')
            msg = msg.split(' ')
            command = msg[0]

            if command == Command.PLAY_VIDEO:
                self._play_video(msg[1:])
            elif command == Command.STOP_VIDEO:
                self._stop_video()

        print(f'Connection to {addr} failed')

    def _play_video(self, msg: List[str]) -> None:
        if self._video_player is not None:
            print('Video player already playing, stopping first...')
            self.stop_video()

        msg = [m.strip() for m in msg]
        keypairs = [keypair.split('=') for keypair in msg]
        kwargs = {keypair[0]: keypair[1] for keypair in keypairs}

        self._video_player = VideoPlayer(
            int(kwargs.get('fps', 10)),
            kwargs.get('image_dir', DEFAULT_IMAGE_DIR)
        )

        Thread(target=self._video_player.start).start()
        #self._video_player.start()

    def _stop_video(self) -> None:
        if self._video_player is None:
            print('No video player active')
            return

        self._video_player.stop()
        # Wait for video player to finish
        while self._video_player.is_playing():
            time.sleep(.05)

        self._video_player = None


if __name__ == '__main__':
    video_player_server = VideoPlayerServer()
    video_player_server.start(IP, PORT)
