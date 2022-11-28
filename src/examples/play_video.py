import sys
from PIL import Image
from typing import List
import os
from pathlib import Path
import time

from display import Display, ST7735R_Display


def get_images(image_dir: str, width: int, height: int) -> List[str]:
    image_names = []

    for image in os.listdir(image_dir):
        # Skip all files not starting with "image"
        #if not image.startswith('image'):
        #    continue

        image_names.append(image)

    def get_image_number(image_name: str) -> int:
        image_extension = '.jpg'
        return int(image_name.split('-')[-1].split(image_extension)[0])

    # Sort images
    image_names = sorted(image_names, key=get_image_number)

    # Create full paths
    image_paths = map(lambda name: Path(image_dir, name), image_names)

    # Create PIL images
    images = [Image.open(image_path) for image_path in image_paths]

    # Resize images to correct dimensions
    images = list(map(lambda image: image.resize((width, height)), images))

    return images


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: play_video.py IMAGE_DIR FPS')
        sys.exit(0)

    width       = 160
    height      = 128
    fps         = int(sys.argv[2])
    frame_delay = 1 / fps

    image_dir = sys.argv[1]
    images    = get_images(image_dir, width, height)

    print(f'Found {len(images)} images')
    print('Starting playing images...')

    display = ST7735R_Display()

    t0 = time.time()
    fps_counter = 0

    while True:

        for nbr, image in enumerate(images):
            before_display = time.time()
            display.show_image(image)
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
            