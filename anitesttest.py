import pygame
import pyganim

back_anim = pyganim.PygAnimation([('resources/img/crono_%s.%s.gif' % ('back_run', str(num).rjust(3, '0')), 100) for num in range(6)])

screen = pygame.display.set_mode((1200, 700))

back_anim.play()

place = pygame.set_rect((20, 20))

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Client_Hero(Entity):
    def __init__(self, pos_x, pos_y, width, height):
        super(Client_Hero, self).__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = height
        self.width = width
        self.image = back_anim


hero = Client_Hero(20, 50, )


while True:
    screen.fill((100, 50, 50))
    back_anim.blit(place, (20, 20))

    pygame.display.update()
