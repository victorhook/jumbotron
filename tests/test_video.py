from pathlib import Path
import sys

ROOT_PATH = Path(__file__).absolute().parent.parent
src = str(ROOT_PATH.joinpath('src'))
leds = str(ROOT_PATH.joinpath('led.csv'))
sys.path.append(src)

image_dir = str(ROOT_PATH.joinpath('videos', 'hocky_30', 'images'))

from videoplayer import VideoPlayer
from led import Led

videoplayer = VideoPlayer(30, image_dir, None, Led())
videoplayer.start()
#videoplayer.pickle()