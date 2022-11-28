from PIL import Image
from pathlib import Path
import os
from typing import List
from threading import Thread, Event
import time
import pygame

from display import ST7735R_Display

pygame_is_initialized = False


class VideoPlayer:

    def __init__(self, fps: int, image_dir: str, audio_dir: str = None,
                 width: int = 160, height: int = 128) -> None:
        self._fps          = fps
        self._image_dir    = image_dir
        self._width        = width
        self._height       = height

        self._display      = ST7735R_Display(width, height)

        self._audio_player = AudioPlayer(audio_dir)
        self._playing      = Event()

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

        t0 = time.time()
        fps_counter = 0
        frame_delay = 1 / self._fps

        audio_thread = Thread(target=self._audio_player.start)
        audio_thread.start()

        while self._playing.is_set():
            
            for image_nbr, image in enumerate(self._images):
                before_display = time.time()
                self._display.show_image(image)
                after_display = time.time()

                dt = after_display - t0            
                fps_counter += 1
                
                if dt > 1:
                    print(f'\rFPS: {fps_counter}')
                    t0 = after_display + (1 - dt)
                    fps_counter = 0

                next_frame = before_display + frame_delay
                if next_frame > after_display:
                    time.sleep(next_frame - after_display)
                
        print('Video player ending')
        audio_thread.join()

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



class AudioPlayer:

    def __init__(self, audio_path: str) -> None:
        self._audio_path = audio_path
        if audio_path is None:
            print('Audio path is None, not playing any audio!')
            return
        
        global pygame_is_initialized
        if not pygame_is_initialized:
            print('Initializing pygame mixer')
            # No clue if all this madness is really needed...
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=4096)
            pygame.mixer.init()
            pygame.init()
            pygame_is_initialized = True

        self._stop = Event()
        self._stop.set()
        self._sound = pygame.mixer.Sound(audio_path)
        print(f'Audio path: {audio_path}')

    def start(self) -> None:
        if self._audio_path is None:
            return

        if self.is_playing():
            print('Audio already playing!')
            return

        self._stop.clear()
        print('Audio starting')

        playing = self._sound.play()
        while playing.get_busy():
            pygame.time.delay(100)
        #self._stop.wait()
            
        print('Stopping!')
        playing.stop()

    def stop(self) -> None:
        if self._audio_path is None:
            return

        if not self.is_playing():
            print('Audio player not playing!')
            return

        self._stop.set()

    def is_playing(self) -> bool:
        return not self._stop.is_set()
