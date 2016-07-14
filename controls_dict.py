import pygame
from pygame.locals import *

controls = {
    "up" : K_w,
    "down": K_s,
    "left": K_a,
    "right": K_d,
    "button1": K_1,
    "button2": K_SPACE,
    "button3": K_3,
}

def cont_imp():
    return controls
