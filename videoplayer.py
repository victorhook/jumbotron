from PIL import Image
from pathlib import Path
import os
from typing import List
from threading import Thread, Event
import pygame

pygame.mixer.init()


class VideoPlayer:

    def __init__(self, fps: int, image_dir: str, audio_dir: str = None,
                 width=128, height=160) -> None:
        self._fps          = fps
        self._image_dir    = image_dir
        self._width        = width
        self._height       = height
        self._frame_delay  = 1 / fps

        self._audio_player = AudioPlayer(audio_dir)
        self._playing      = Event()

    def _get_images(self, image_dir: str, width: int, height: int) -> List[str]:
        image_names = []

        for image in os.listdir(image_dir):
            # Skip all files not starting with "image"
            if not image.startswith('image'):
                continue

            image_names.append(image)

        def get_image_number(image_name: str) -> int:
            image_extension = '.jpg'
            return int(image_name.split('-')[-1].split(image_extension)[0])

        # Sort images
        image_names = sorted(image_names, key=get_image_number)
        print(f'Found {len(image_names)} images for video...')

        # Create full paths
        image_paths = map(lambda name: Path(image_dir, name), image_names)

        # Create PIL images
        print(f'Creating PIL image objects...')
        images = [Image.open(image_path) for image_path in image_paths]

        # Resize images to correct dimensions
        print(f'Resizing images to dimensions {width}x{height}...')
        images = list(map(lambda image: image.resize((width, height)), images))

        print('Image preprocessing complete!')
        return images

    def start(self) -> None:
        if self._playing.is_set():
            print('Video already playing!')
            return

        # Set flag that we've started
        self._playing.set()

        # Get all images
        self._images = self._get_images(self._image_dir, self._width, self._height)

        # Can happen if user aborts play before we've finished processing the images
        if not self.is_playing():
            return

        print('Video player starting')
        self._audio_player.start()

        while self._playing.is_set():
            self._show_frame()

        print('Video player ending')

    def stop(self) -> None:
        print(self._playing.is_set())
        if not self._playing.is_set():
            print('Video not playing!')
            return

        self._audio_player.stop()
        self._playing.clear()

    def is_playing(self) -> bool:
        return self._playing.is_set()

    def _show_frame(self) -> None:
        import time
        #print(time.time())
        time.sleep(.5)



class AudioPlayer:

    def __init__(self, audio_dir: str) -> None:
        self._audio_dir = audio_dir
        if audio_dir is None:
            print('Audio dir is None!')
            return

        self._stop = Event()
        self._stop.set()
        self._sound = pygame.mixer.Sound(audio_dir)

    def start(self) -> None:
        if self._audio_dir is None:
            return

        if self.is_playing():
            print('Audio already playing!')
            return

        self._stop.clear()
        print('Audio starting')

        playing = self._sound.play()
        while playing.get_busy():
            #self._stop.wait()
            pygame.time.delay(100)

    def stop(self) -> None:
        if self._audio_dir is None:
            return

        if not self.is_playing():
            print('Audio player not playing!')
            return

        self._stop.set()

    def is_playing(self) -> bool:
        return not self._stop.is_set()