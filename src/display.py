import digitalio
import board
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7735
import sys
import busio


class Display:

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def show_image(self, image: Image) -> None:
        pass


class ST7735R_Display(Display):
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        # Configuration for CS and DC pins
        cs_pin    = digitalio.DigitalInOut(board.CE0)
        dc_pin    = digitalio.DigitalInOut(board.D24)
        reset_pin = digitalio.DigitalInOut(board.D25)

        BAUDRATE = 60000000

        # Setup SPI bus using hardware SPI:
        spi = board.SPI()

        self._disp = st7735.ST7735R(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
            rotation=270
        )

        self._image = Image.new("RGB", (self._disp.width, self._disp.height))
        self._draw = ImageDraw.Draw(self._image)

    def show_image(self, image: Image) -> None:
        # Display image.
        self._disp.image(image)
        