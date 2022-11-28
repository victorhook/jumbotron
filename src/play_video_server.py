import socket
import sys
from typing import List
import time
from threading import Thread

# Hardware
from videoplayer import VideoPlayer, AudioPlayer
from led import Led


IP   = '0.0.0.0'
PORT = 9999

DEFAULT_IMAGE_DIR = '.'
DEFAULT_AUDIO     = 'audio.wav'
DEFAULT_COLOR     = '#ffffff'


class VideoPlayerServer:
    
    def __init__(self) -> None:
        self._sock: socket.socket = None
        self._video_player: VideoPlayer = None
        self._audio_player: AudioPlayer = None
        self._leds = Led()
        self._leds.set_color(DEFAULT_COLOR)
        
        self._command_handlers = {
            'PLAY_VIDEO': self._cmd_play_video,
            'STOP_VIDEO': self._cmd_stop_video,
            'PLAY_AUDIO': self._cmd_play_audio,
            'STOP_AUDIO': self._cmd_stop_audio,
            'SET_LED':    self._cmd_set_led
        }

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
            try:
                msg = con.recv(1024)

                if not msg:
                    connected = False
                    continue

                msg = msg.decode('utf-8')
                msg = msg.split(' ')
                command = msg[0]
                
                if len(msg) > 1:
                    kwargs = [m.strip() for m in msg[1:]]
                    keypairs = [keypair.split('=') for keypair in kwargs]
                    kwargs = {keypair[0]: keypair[1] for keypair in keypairs}
                else:
                    kwargs = {}
            
                if command not in self._command_handlers:
                    err = f'Failed to recognize command {command}!\n'
                    print(err)
                    con.send(err.encode('utf-8'))
                    continue

                # Call appropiate command handler
                command_handler = self._command_handlers[command]
                print(f'Command: {command} with kwargs: {kwargs}, command-handler: {command_handler.__name__}')
                Thread(target=command_handler, args=(kwargs, )).start()
                
                con.send(f'{command} OK\n'.encode('utf-8'))
            except ConnectionResetError as e:
                # Nothing to do..
                pass

        print(f'Connection to {addr} failed')

    # -- Command handlers -- #
    def _cmd_play_video(self, kwargs: dict) -> None:
        if self._video_player is not None:
            print('Video player already playing, stopping first...')
            self._cmd_stop_video()

        self._video_player = VideoPlayer(
            int(kwargs.get('fps', 10)),
            kwargs.get('image_dir', DEFAULT_IMAGE_DIR)
        )

        self._video_player.start()

    def _cmd_stop_video(self, kwargs: dict) -> None:
        if self._video_player is None:
            print('No video player active')
            return

        self._video_player.stop()
        # Wait for video player to finish
        while self._video_player.is_playing():
            time.sleep(.05)

        self._video_player = None

    def _cmd_play_audio(self, kwargs: dict) -> None:
        if self._audio_player is not None:
            print('Audio player already playing, stopping first...')
            self._cmd_stop_audio(kwargs)

        self._audio_player = AudioPlayer(kwargs.get('audio', DEFAULT_AUDIO))
        self._audio_player.start()

    def _cmd_stop_audio(self, kwargs: dict) -> None:
        if self._audio_player is None:
            print('No audio player active')
            return

        self._audio_player.stop()
        # Wait for video player to finish
        while self._audio_player.is_playing():
            time.sleep(.05)

        self._audio_player = None
        
    def _cmd_set_led(self, kwargs: dict) -> None:
        self._leds.set_color(kwargs.get('color', DEFAULT_COLOR))



if __name__ == '__main__':
    video_player_server = VideoPlayerServer()
    video_player_server.start(IP, PORT)
