import sys
from PIL import Image
from typing import List
import os
from pathlib import Path
import time
from tkinter import tk


class Display:

    def show_image(self, image: Image) -> None:
        pass


class TkDisplay(Display):

    def __init__(self) -> None:
        root = tk.Tk()

    def show_image(self, image: Image) -> None:
        pass



def get_images(image_dir: str, width: int, height: int) -> List[str]:
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

    # Create full paths
    image_paths = map(lambda name: Path(image_dir, name), image_names)

    # Create PIL images
    images = [Image.open(image_path) for image_path in image_paths]

    # Resize images to correct dimensions
    images = list(map(lambda image: image.resize((width, height)), images))

    return images


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Must give image directory as input!')
        sys.exit(0)

    width       = 128
    height      = 160
    fps         = 10
    frame_delay = 1 / fps

    image_dir = sys.argv[1]
    images    = get_images(image_dir, width, height)

    print(f'Found {len(images)} images')
    print('Starting playing images...')

    display = Display()

    while True:

        for nbr, image in enumerate(images):
            print(f'Frame: {nbr}')

            t0 = time.time()
            display.show_image(image)

            next_frame = t0 + frame_delay
            now = time.time()

            if next_frame > now:
                time.sleep(next_frame - now)

