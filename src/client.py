import socket
from queue import Queue
from threading import Thread, Event
import traceback


SERVER_IP   = '127.0.0.1'
SERVER_PORT = 9999


class Client:

    def __init__(self) -> None:
        self._sock: socket.socket = None

    def __enter__(self) -> 'Client':
        self.connect()
        return self
    
    def __exit__(self, *_) -> None:
        self.disconnect()
    
    def disconnect(self) -> None:
        if self._sock is not None:
            self._sock.close()
        self._sock = None
        
    def connect(self) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((SERVER_IP, SERVER_PORT))
            self._sock = sock
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False
        
    def _send(self, msg: str) -> None:
        if self._sock is None:
            raise RuntimeError('Client must be connected first!')
        
        tx = msg.encode('utf-8')
        self._sock.send(tx)
        rx = self._sock.recv(1024).decode('utf-8')
        print(f'TX: {msg}')
        print(f'RX: {rx}')
        
    def play_video(self, image_dir: str, fps: int) -> None:
        self._send(f'PLAY_VIDEO image_dir={image_dir} fps={fps}')

    def stop_video(self) -> None:
        self._send('STOP_VIDEO')

    def play_audio(self, audio_path: str) -> None:
        self._send(f'PLAY_AUDIO audio={audio_path}')

    def stop_audio(self) -> None:
        self._send('STOP_AUDIO')
        
    def set_led(self, color: str) -> None:
        self._send(f'SET_LED led={color}')
