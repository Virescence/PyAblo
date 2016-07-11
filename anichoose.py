import sys
import pygame
import pyganim

pygame.init()

class DefineAnimations():
    def __init__(self):
        self.front_standing = pygame.image.load('resources/img/crono_front.gif')
        self.back_standing = pygame.image.load('resources/img/crono_back.gif')
        self.left_standing = pygame.image.load('resources/img/crono_left.gif')
        self.right_standing = pygame.transform.flip(self.left_standing, True, False)
        self.keyimg = pygame.image.load('resources/img/crono_keyimg.gif')
        self.animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
        self.animObjs = {}
        for self.animType in self.animTypes:
            self.imagesAndDurations = [('resources/img/crono_%s.%s.gif' % (self.animType, str(num).rjust(3, '0')), 100)
                                for num in range(6)]
            self.animObjs[self.animType] = pyganim.PygAnimation(self.imagesAndDurations)

        # create the right-facing sprites by copying and flipping the left-facing sprites
        self.animObjs['right_walk'] = self.animObjs['left_walk'].getCopy()
        self.animObjs['right_walk'].flip(True, False)
        self.animObjs['right_walk'].makeTransformsPermanent()
        self.animObjs['right_run'] = self.animObjs['left_run'].getCopy()
        self.animObjs['right_run'].flip(True, False)
        self.animObjs['right_run'].makeTransformsPermanent()
        self.animObjs['front_standing'] = self.front_standing
        self.animObjs['back_standing'] = self.back_standing
        self.animObjs['left_standing'] = self.left_standing
        self.animObjs['right_standing'] = self.right_standing

def pick(change_x, change_y):

    if change_x > 1 and not change_x > 25:
        return 'right_walk'
    elif change_x > 25:
        return 'right_run'
    elif change_x < -1 and not change_x < -25:
        return 'left_walk'
    elif change_x < -25:
        return 'left_run'
    else:
        return 'front_walk'