import board
from collections import namedtuple
import neopixel
from typing import Tuple
import time

NBR_OF_LEDS = 4

Color = namedtuple('Color', ['r', 'g', 'b'])


class Led:

    def __init__(self) -> None:
        self._leds = neopixel.NeoPixel(board.D12, NBR_OF_LEDS)

    def set_color_single_led(self, led_nbr: int, color: str) -> None:
        ''' Color is string, as hex. led_nbr starts at 1! '''
        self._leds[led_nbr-1] = self._hex_color_to_tuple(color)

    def set_color(self, color: str) -> None:
        ''' Color is string, as hex. '''
        self._leds.fill(self._hex_color_to_tuple(color))

    def _hex_color_to_tuple(self, color: str) -> Color:
        color = color.split('#')[-1]
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        return Color(r, g, b)
