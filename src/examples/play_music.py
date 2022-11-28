import pygame
import sys

pygame.mixer.init()
sound = pygame.mixer.Sound('audio.wav')
playing = sound.play()
while playing.get_busy():
    pygame.time.delay(100)