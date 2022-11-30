from collections import namedtuple
from PIL import Image
from pathlib import Path
import os
from typing import List
from threading import Thread, Event
import time
import pygame
import csv
from led import Led

from display import ST7735R_Display

pygame_is_initialized = False

DEFAULT_LED_CSV   = str(Path(__file__).absolute().parent.parent.joinpath('led.csv'))


class VideoPlayer:

    def __init__(self, fps: int, image_dir: str, audio_dir: str = None,
                 leds: Led = None, width: int = 160, height: int = 128) -> None:
        self._fps          = fps
        self._image_dir    = image_dir
        self._width        = width
        self._height       = height

        self._display      = ST7735R_Display(width, height)

        self._audio_player = AudioPlayer(audio_dir)
        self._led_player   = LedPlayer(leds)
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
        led_thread = Thread(target=self._led_player.start)
        #audio_thread.start()
        led_thread.start()

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
                    
                if not self.is_playing():
                    break

        print('Video player ending')
        #audio_thread.join()
        led_thread.join()

    def stop(self) -> None:
        print(self._playing.is_set())
        if not self._playing.is_set():
            print('Video not playing!')
            return

        self._audio_player.stop()
        self._led_player.stop()
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
            pygame.mixer.init()
            pygame_is_initialized = True

        self._is_playing = False
        self._sound = pygame.mixer.Sound(audio_path)
        print(f'Audio path: {audio_path}')

    def start(self) -> None:
        if self._audio_path is None:
            return

        if self.is_playing():
            print('Audio already playing!')
            return

        print('Audio starting')
        self._is_playing = True

        playing = self._sound.play()
        while playing.get_busy() and self.is_playing():
            pygame.time.delay(100)

        print('Audio stopping')
        playing.stop()

    def stop(self) -> None:
        if self._audio_path is None:
            return

        if not self.is_playing():
            print('Audio player not playing!')

        self._is_playing = False

    def is_playing(self) -> bool:
        return self._is_playing


LED_NUMBER_ALL = 0
LedState = namedtuple('LedState', ['color', 'time', 'led_nbr'])


class LedPlayer:
    
    def __init__(self, leds: 'Led') -> None:
        self.leds = leds
        self._running = False
        
    def start(self, led_csv: str = DEFAULT_LED_CSV) -> None:
        if not os.path.exists(led_csv):
            print(f'Led csv {led_csv} doesnt exists!')
            return

        led_states = self._parse_led_states(led_csv)
        state_index = 0
        self._running = True
        time_offset = 0.0
        
        print('Led player starting')
        
        while self._running:
            led_state = led_states[state_index]
            
            if led_state.led_nbr == LED_NUMBER_ALL:
                self.leds.set_color(led_state.color)
            else:
                self.leds.set_color_single_led(led_state.led_nbr, led_state.color)

            # Peek at next state
            next_state_index = (state_index + 1) % len(led_states)
            next_state = led_states[next_state_index]

            next_state_change = next_state.time + time_offset
            dt = next_state_change - time.time()
            #print(f'{led_state.color} -> {next_state.color}: {dt:.5}')
            
            if dt > 0:
                time.sleep(dt)
            
            # Change to next state
            state_index = next_state_index
            
            if state_index == 0:
                time_offset = time.time()
                
    def stop(self) -> None:
        if not self._running:
            print('Led player not running')
            
        self._running = False

    def _parse_led_states(self, led_csv: str) -> List[LedState]:
        with open(led_csv) as f:
            data = list(csv.reader(f))
            data = list(filter(len, data))

        header = data[0]
        led_states = []
        for line in data[1:]:
            line = [word.strip() for word in line]
            led_states.append(LedState(
                line[0],
                float(line[1]),
                int(line[2]),
            ))
            
        return led_states
        
       
       
if __name__ == '__main__':
    from led import Led
    ledplayer = LedPlayer(Led())
    ledplayer.start('/home/victor/projects/gingerbreadhouse-2022/src/led.csv')