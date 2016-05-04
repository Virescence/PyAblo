import sys
import pygame
import pyganim

pygame.init()

def pick(grounded, right, left, action1):

    # load the "standing" sprites (these are single images, not animations)
    front_standing = pygame.image.load('resources/img/crono_front.gif')
    back_standing = pygame.image.load('resources/img/crono_back.gif')
    left_standing = pygame.image.load('resources/img/crono_left.gif')
    right_standing = pygame.transform.flip(left_standing, True, False)

    # creating the PygAnimation objects for walking/running in all directions
    animTypes = 'back_run back_walk front_run front_walk left_run left_walk'.split()
    animObjs = {}
    for animType in animTypes:
        imagesAndDurations = [('resources/img/crono_%s.%s.gif' % (animType, str(num).rjust(3, '0')), 100) for num in range(6)]
        animObjs[animType] = pyganim.PygAnimation(imagesAndDurations)

    # create the right-facing sprites by copying and flipping the left-facing sprites
    animObjs['right_walk'] = animObjs['left_walk'].getCopy()
    animObjs['right_walk'].flip(True, False)
    animObjs['right_walk'].makeTransformsPermanent()
    animObjs['right_run'] = animObjs['left_run'].getCopy()
    animObjs['right_run'].flip(True, False)
    animObjs['right_run'].makeTransformsPermanent()
    animObjs['front_standing'] = front_standing
    animObjs['back_standing'] = back_standing
    animObjs['left_standing'] = left_standing
    animObjs['right_standing'] = right_standing

    # have the animation objects managed by a conductor.
    # With the conductor, we can call play() and stop() on all the animtion
    # objects at the same time, so that way they'll always be in sync with each
    # other.
    # moveConductor = pyganim.PygConductor(animObjs)

    WHITE = (255, 255, 255)
    BGCOLOR = (100, 50, 50)

    print(animObjs)
    return animObjs['front_walk']



"""
if moveUp or moveDown or moveLeft or moveRight:
    # draw the correct walking/running sprite from the animation object
    moveConductor.play()  # calling play() while the animation objects are already playing is okay; in that case play() is a no-op
    if running:
        if direction == UP:
            return animObjs['back_run']
        elif direction == DOWN:
            return animObjs['front_run']
        elif direction == LEFT:
            return animObjs['left_run']
        elif direction == RIGHT:
            return animObjs['right_run']
    else:
        # walking
        if direction == UP:
            return animObjs['back_walk']
        elif direction == DOWN:
            return animObjs['front_walk']
        elif direction == LEFT:
            return animObjs['left_walk']
        elif direction == RIGHT:
            return animObjs['right_walk']

else:
    # standing still
    moveConductor.stop()  # calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
    if direction == UP:
        return back_standing
    elif direction == DOWN:
        return front_standing
    elif direction == LEFT:
        return left_standing
    elif direction == RIGHT:
        return right_standing









def pick(grounded, right, left, action1):
    if grounded:
        return pygame.image.load('resources/img/crono_front.gif')
    elif action1:
        return pygame.image.load('resources/img/crono_back.gif')
    elif left:
        return pygame.image.load('resources/img/crono_left.gif')
    elif right:
        leftImg = pygame.image.load('resources/img/crono_left.gif')
        return pygame.transform.flip(leftImg, True, False)
    else:
        return pygame.image.load('resources/img/crono_sleep.000.gif')

    self.image = anichoose.pick(self.grounded, self.right, self.left, self.action1)
    print(self.grounded, self.right, self.left, self.action1)
    self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
"""