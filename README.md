## Wire connection
1. GND
2. 5V
3. SCK (SPI Clock)
4. SDA (SPI MOSI)
5. RES (Reset)
6. RS
7. CS (SPI CS, Chip Select)
8. LEDA (Background light)
9. WS2812 LED data

## Pin connections
| Pin number | Meaning | Pin on Raspberry pi | Color |
| --- | --- | --- |
| 1 | GND | GND | Black |
| 2 | 5V | 5V |
| 3 | SCK (SPI Clock) | GPIO11 (SPI0_CLK) |
| 4 | SDA (SPI MOSI) | GPIO10 (SPI0_MOSI) |
| 5 | RES (Reset) | GPIO25 |
| 6 | RS | GPIO24 |
| 7 | CS (SPI CS, Chip Select) | GPIO8 (SPI0_CE0_N) |
| 8 | LEDA (Background light) | 3V |
| 9 | WS2812 LED data | GPIO12 (PWM) | Red |