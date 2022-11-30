import socket
import traceback
import logging


SERVER_IP   = '127.0.0.1'
SERVER_PORT = 9999

logger = logging.getLogger(__name__)


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
            logger.info(traceback.format_exc())
            return False

    def _send(self, msg: str) -> None:
        if self._sock is None:
            logger.info('Client must be connected first, trying to connect...')
            if not self.connect():
                logger.info('Failed to connect!')
                return

        tx = msg.encode('utf-8')
        self._sock.send(tx)
        rx = self._sock.recv(1024).decode('utf-8')
        logger.info(f'TX: {msg}')
        logger.info(f'RX: {rx}')

    def play_video(self, image_dir: str, fps: int, audio_path: str = None) -> None:
        cmd = f'PLAY_VIDEO image_dir={image_dir} fps={fps}'
        if audio_path is not None:
            cmd += f' audio={audio_path}'
        self._send(cmd)

    def stop_video(self) -> None:
        self._send('STOP_VIDEO')

    def play_audio(self, audio_path: str) -> None:
        self._send(f'PLAY_AUDIO audio={audio_path}')

    def stop_audio(self) -> None:
        self._send('STOP_AUDIO')

    def set_led(self, color: str) -> None:
        self._send(f'SET_LED led={color}')
