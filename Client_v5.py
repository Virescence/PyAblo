import json
import pygame
from pygame.locals import *
import random
import sys
import socket
import threading
import textwrap
import time
import pyganim




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

    def pick(self, change_x, change_y):

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

# RICKY, CLEAN THIS UP, SO MESSY :( :( :( :(
# Am I wasting memory by loading and playing all images?
defineanimations = DefineAnimations()
for key in defineanimations.animObjs:
    try:
        defineanimations.animObjs[key].play()
    except:
        pass
# CLEAN ME & && & * * * & ^ ^^



class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def sendData(self, data):
        self.sock.sendto(data.encode(), ("wiesen.tech", 1234))
        # print("sent: " + repr(data))

    # def sendAuth(self, data):
        # self.sock.sendto(data.encode(), ("localhost", 1235))

    def recvData(self):
        while True:
            try:
                data = self.sock.recv(8192)
                # print("recv data: " + repr(data))
                if data:
                    self.dataHandler(data)
            except Exception as e:
                print("Failed at line 85")
                pass

    def dataHandler(self, data):
        if data[:4] == b'^id^':
            data = data.decode()

        elif data[:4] == b'^db^':
            data = data.decode()
            chatfsm.authenticate(data[4:])

        elif data[:2] == b'^^':
            data = data.decode()
            chatclass.update(data[10:])

        elif data[:4] == b'TILE':
            if not clientmap.complete:
                data = data.decode()
                data = data[4:]
                clientmap.update(data)

        elif data == b'HeroReq':
            client.sendData("INIT" + json.dumps(game.hero.object_dict))

        elif data[:2] == b'>>':
            game.hero.assign_obj_id(data[2:])

        elif data[:2] == b'*^':
            data = data[2:].decode()
            data = json.loads(data)
            self.remoteobjectHandler(data)

        elif data[:6] == b'^INIT^':
            data = data[6:].decode()
            data = json.loads(data)
            self.remoteobjectCreator(data)

        elif data[:4] == b'^ATK':
            data = json.loads(data[4:].decode())
            RemoteAttackObject(data[0], data[1], data[2])


        else:
            print("UNKNOWN DATA WHY ARE YOU GIVING THIS TO ME")
            # data = data.decode()
            # data = json.loads(data)
            # object_handler(data)

    def remoteobjectCreator(self, data):
        if not data["obj_id"] in game.id_to_object:
            RemoteHero(data["pos_x"], data["pos_y"], data["width"], data["height"], data["color"], data["name"],
                       data["obj_id"])

    def remoteobjectHandler(self, data):
        pos_x = data[0][0]
        pos_y = data[0][1]
        obj_id = data[1]
        hp = data[2]
        if not obj_id == game.hero.obj_id:
            game.id_to_object[obj_id].update(pos_x, pos_y, hp)


class Chat:
    def __init__(self):
        self.displayed_chat = []
        self.all_chat = []
        self.modifier = 0
        self.username = ""

    def modifier_change(self, value):
        self.modifier += value
        if self.modifier < 0:
            self.modifier = 0

    def update(self, data):
        if data != "placeholder":
            # First, let's dump whatever data we have into "all_chat"
            self.all_chat.append(data)
            # Let's wrap the text
            wrapped_text = textwrap.wrap(data, 20)
            for string in wrapped_text:
                self.displayed_chat.append(string)
        # Now, let's make sure we don't ~~display~~ save too much
        if len(self.displayed_chat) > 250:
            self.displayed_chat = self.displayed_chat[len(self.displayed_chat) - 250:]

        # Kill anything that's already been displayed...
        for msg in chat:
            msg.kill()
        # And display what we've got!
        line = ((len(self.displayed_chat) - 1) - self.modifier)
        y_pos = chatboxupper.rect.bottomleft[1]
        while line >= ((len(self.displayed_chat) - 25) - self.modifier):
            if line < 0:
               break
            try:
                UIText(chatboxupper.rect.bottomleft[0], y_pos, self.displayed_chat[line], (255, 255, 255), "chat")
                line -= 1
                y_pos -= 18
            except:
                break


class Game:
    def __init__(self):
        self.font1 = pygame.font.Font('resources/Fonts/courier.ttf', 16)
        self.font2 = pygame.font.Font('resources/Fonts/Pixel.ttf', 14)
        self.hero = None
        self.client_list = []
        self.obj_list = []
        self.id_to_object = {}

    def make_hero(self, pos_x, pos_y, width, height, color, name, obj_id):
        self.hero = ClientHero(pos_x, pos_y, width, height, color, name, obj_id)


class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class UIElement(Entity):
    def __init__(self, pos_x, pos_y, width, height, color, obj_id=None):
        super(UIElement, self).__init__()
        self.obj_id = obj_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = height
        self.width = width
        self.color = color
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((color))
        self.rect = self.image.get_rect(bottomleft=((self.pos_x, self.pos_y)))
        ui_elements.add(self)


class UIBase(UIElement):
    def __init__(self):
        super(UIBase, self).__init__(self)


class UIPicture(Entity):
    def __init__(self, pos_x, pos_y, image, loading=False):
        super(UIPicture, self).__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = pygame.image.load(image)
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        if loading:
            loading_images.add(self)
        else:
            ui_pictures.add(self)


class UIText(Entity):
    def __init__(self, pos_x, pos_y, text, fontcolor, type):
        super(UIText, self).__init__()
        self.type = type
        self.text = text
        self.fontcolor = fontcolor
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.font = game.font1
        self.image = self.font.render(self.text, True, fontcolor)
        self.rect = self.image.get_rect(bottomleft=((self.pos_x, self.pos_y)))
        if self.type == "chat":
            chat.add(self)
        if self.type == "UI":
            ui_text.add(self)
        if self.type == "not_type":
            not_type.add(self)
        if self.type == "live_chat":
            live_chat.add(self)

    def update(self, newtext, max_x=2500):
        self.max_x = max_x
        self.image = self.font.render(newtext, True, self.fontcolor)
        self.rect = self.image.get_rect(bottomleft=((self.pos_x, self.pos_y)))
        if self.rect.bottomright[0] > self.max_x:
            self.rect.x -= (self.rect.bottomright[0] - self.max_x)


class HeroName(Entity):
    def __init__(self, pos_x, pos_y, name, daddy):
        super(HeroName, self).__init__()
        self.daddy = daddy
        self.name = name
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.font = game.font2
        self.image = self.font.render(self.name, True, (255, 255, 255))
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        nameplates.add(self)

    def update(self):
        self.rect.midbottom = (self.daddy.rect.midbottom[0], self.daddy.rect.midbottom[1] - 120)


class HealthBar(Entity):
    def __init__(self, daddy):
        super(HealthBar, self).__init__()
        self.daddy = daddy
        self.pos_x = daddy.pos_x
        self.pos_y = daddy.pos_y
        self.image = pygame.image.load('resources/Health/H10.gif')
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        nameplates.add(self)

    def update(self):
        self.rect.midbottom = (self.daddy.rect.midbottom[0], self.daddy.rect.midbottom[1] - 95)
        self.image = pygame.image.load('resources/Health/H' + repr(self.daddy.curr_hp) + '.gif')


class RemoteHero(Entity):
    def __init__(self, pos_x, pos_y, width, height, color, name, obj_id):  # add NAME
        super(RemoteHero, self).__init__()
        self.name = name
        game.client_list.append(self.name)
        self.obj_id = obj_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = height
        self.width = width
        self.color = color
        self.curr_hp = 10
        # self.image = pygame.Surface([self.width, self.height])
        # self.image.fill((color))
        self.image = defineanimations.keyimg
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        self.anim = defineanimations.animObjs['back_walk']
        self.hero_name = HeroName(self.pos_x, self.pos_y, self.name, self)
        self.health_bar = HealthBar(self)
        heroes.add(self)
        remote_heroes.add(self)
        game.id_to_object[self.obj_id] = self
        self.change_x = 0
        self.change_y = 0

    def update(self, pos_x, pos_y, hp):
        self.change_x = pos_x - self.rect.x
        self.change_y = pos_y - self.rect.y
        self.rect.x = pos_x
        self.pos_x = pos_x
        self.rect.y = pos_y
        self.pos_y = pos_y
        self.curr_hp = hp
        self.hero_name.update()
        self.health_bar.update()

        anichoice = defineanimations.pick(self.change_x, self.change_y)
        self.anim = defineanimations.animObjs[anichoice]
        #Not sure how to keep previous position data
        #What if, in addition to position, we send the change variables over also.
        #Else, maybe it's ok for the sprites to look like they're sprinting to get to wherever they are if there's lag!


class ClientHero(Entity):
    def __init__(self, pos_x, pos_y, width, height, color, name, obj_id):
        super(ClientHero, self).__init__()
        self.name = name
        game.client_list.append(self.name)
        self.obj_id = obj_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = 76 # self.height = height
        self.width = 40 # self.width = width
        self.color = color
        self.image = defineanimations.keyimg
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        self.anim = defineanimations.animObjs['front_walk']
        self.hero_name = HeroName(self.pos_x, self.pos_y, self.name, self)
        self.health_bar = HealthBar(self)
        self.max_hp = 10
        self.curr_hp = self.max_hp
        self.previous_x = None
        self.previous_y = None
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.action1 = False
        self.action2 = False
        self.action3 = False
        self.grounded = False
        self.cooldown1 = False
        self.cooldown2 = False
        self.current_direction = "Right"
        self.gcd = 3
        self.atk_cd = .25
        self.hp_cd = 3
        self.gravity_staller = 5 + time.time()
        self.dt1 = time.time() + self.gcd
        self.dt2 = time.time() + self.atk_cd
        self.hp_dt = time.time()
        self.recharging = False
        self.change_x = 0
        self.change_y = 0
        heroes.add(self)
        self.object_dict = {"pos_x": self.rect.x, "pos_y": self.rect.y, "width": self.width, "height": self.height,
                            "color": self.color, "name": self.name, "obj_id": self.obj_id}

    def assign_obj_id(self, obj_id): # depreciated
        self.obj_id = int(obj_id)
        self.object_dict = {"pos_x": self.rect.x, "pos_y": self.rect.y, "width": self.width, "height": self.height,
                            "color": self.color, "name": self.name, "obj_id": self.obj_id}

        identifier.known_objects.append(self.obj_id)

    def gravity(self):
        if chatfsm.map_loaded:
            if self.grounded:
                return None
            elif self.change_y == 0:
                self.change_y = .5
            else:
                self.change_y += .5

    def health_recharge_fsm(self):
        if self.curr_hp < self.max_hp:
            if time.time() >= self.hp_dt + self.hp_cd:
                self.curr_hp += 1
                self.send_update()

    def update(self):
        if self.cooldown1:
            if time.time() > self.dt1:
                self.dt1 = time.time() + self.gcd
                self.cooldown1 = False

        if self.cooldown2:
            if time.time() > self.dt2:
                self.dt2 = time.time() + self.atk_cd
                self.cooldown2 = False

        self.health_recharge_fsm()
        self.gravity()
        self.moving_left = False
        self.moving_right = False
        if self.up and self.grounded:
            self.change_y += -10
            self.grounded = False
        elif self.down and not self.grounded:
            self.change_y += .5
        elif self.left:
            self.moving_left = True
            self.current_direction = "left"
            if self.change_x < -20:
                self.change_x += 6
            elif self.change_x < -7:
                self.change_x += 1
            else:
                self.change_x += -1
        elif self.right:
            self.moving_right = True
            self.current_direction = "right"
            if self.change_x > 20:
                self.change_x += -6
            elif self.change_x > 7:
                self.change_x += -1
            else:
                self.change_x += 1
        if self.change_x < 0 and not self.moving_left:
            self.change_x += 1
        if self.change_x > 0 and not self.moving_right:
            self.change_x += -1

        if self.action1:
            self.action1 = False
            if self.moving_left:
                self.change_x += -25
            if self.moving_right:
                self.change_x += 25

        if self.action2:
            self.action2 = False
            AttackObject(self, self.current_direction)
        self.rect.x += self.change_x
        col_list = pygame.sprite.spritecollide(self, collide, False)
        if len(col_list) == 0:
            self.grounded = False
        else:
            for x in col_list:
                if self.rect.colliderect(x.rect):
                    if self.change_x > 0:
                        self.rect.right = x.rect.left
                        self.change_x = 0

                    if self.change_x < 0:
                        self.rect.left = x.rect.right
                        self.change_x = 0

        self.rect.y += self.change_y
        col_list = pygame.sprite.spritecollide(self, collide, False)
        if len(col_list) > 0:
            for x in col_list:
                if self.change_y > 0:
                    self.rect.bottom = x.rect.top
                    self.change_y = 0
                    self.grounded = True

                if self.change_y < 0:
                    self.rect.top = x.rect.bottom
                    self.change_y = 0

        anichoice = defineanimations.pick(self.change_x, self.change_y)
        self.anim = defineanimations.animObjs[anichoice]

        self.hero_name.update()
        self.health_bar.update()
        if self.rect.x != self.previous_x or self.rect.y != self.previous_y:
            self.previous_x = self.rect.x
            self.previous_y = self.rect.y
            self.send_update()

    def actionfsm(self, event=None, keys=None, mods=None,  chatting=False):
            if event.type == KEYDOWN:
                if mods & KMOD_SHIFT and not self.action1:
                    if not self.cooldown1:
                        self.action1 = True
                        self.cooldown1 = True
                if keys[controls["up"]] and not self.up:
                    self.up = True
                elif keys[controls["down"]] and not self.down:
                    self.down = True
                elif keys[controls["left"]] and not self.left:
                    self.left = True
                elif keys[controls["right"]] and not self.right:
                    self.right = True
                elif keys[controls["button2"]] and not self.action2:
                    if not self.cooldown2:
                        self.action2 = True
                        self.cooldown2 = True

            if event.type == KEYUP:
                if not mods & KMOD_SHIFT and self.action1:
                    self.action1 = False
                if event.key == pygame.K_w and self.up:
                    self.up = False
                elif event.key == pygame.K_s and self.down:
                    self.down = False
                elif event.key == pygame.K_a and self.left:
                    self.left = False
                elif event.key == pygame.K_d and self.right:
                    self.right = False

    def damagetaken(self, damage):
        self.curr_hp -= damage
        self.hp_dt = time.time()
        self.send_update()
        if self.curr_hp < 1:
            self.rect.y = 0
            self.curr_hp = 10

    def send_update(self):
        data = [(self.rect.x, self.rect.y), self.obj_id, self.curr_hp]
        client.sendData(("*^" + json.dumps(data)))


class AttackObject(Entity):
    def __init__(self, daddy, direction):
        super(AttackObject, self).__init__()
        self.direction = direction
        if self.direction == "left":
            self.pos_x = daddy.rect.midleft[0] + 10
        else:
            self.pos_x = daddy.rect.midright[0] + -10
        self.pos_y = daddy.rect.y + 30
        self.color = (100, 255, 0)
        self.distance_traveled = 0
        self.image = pygame.Surface([5, 2])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        attk_objects.add(self)
        client.sendData("^ATK" + json.dumps([self.pos_x, self.pos_y, self.direction]))

    def get_angle(self, mouse_coordinates):
        offset = (mouse_coordinates[1] - (screen.screen_y / 2), mouse_coordinates[0] - (screen.screen_x / 2))

    def update(self):
        if self.distance_traveled > 500:
            self.kill()
            return None
        if self.direction == "left":
            self.rect.x += -25
        elif self.direction == "right":
            self.rect.x += 25
        self.distance_traveled += 25
        if pygame.sprite.spritecollideany(self, remote_heroes):
            self.kill()


class RemoteAttackObject(Entity):
    def __init__(self, pos_x, pos_y, direction):
        super(RemoteAttackObject, self).__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.color = (100, 255, 0)
        self.direction = direction
        self.distance_traveled = 0
        self.image = pygame.Surface([5, 2])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        attk_objects.add(self)

    def update(self):
        if self.distance_traveled > 500:
            self.kill()
        elif self.direction == "left":
            self.rect.x += -25
        elif self.direction == "right":
            self.rect.x += 25
        self.distance_traveled += 25
        target = pygame.sprite.spritecollideany(self, heroes)
        if target:
            if target == game.hero:
                game.hero.damagetaken(2)
            self.kill()


class Tile(Entity):
    def __init__(self, pos_x, pos_y, tile):
        super(Tile, self).__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.tile = tile
        self.image = pygame.Surface([50, 50])
        self.rect = self.image.get_rect(bottomleft=((self.pos_x, self.pos_y)))
        # if self.tile == "0":
            # self.image = pygame.image.load('resources\X.png')
            # self.image.set_colorkey((255, 255, 255), RLEACCEL)
            # tiles.add(self)
            # nocollide.add(self)
        if self.tile == "1":
            self.image = pygame.image.load('resources\C.png')
            self.image.set_colorkey((255, 255, 255), RLEACCEL)
            tiles.add(self)
            collide.add(self)


class Attack(Entity): #OOOOLLLLLDDDDDDD
    def __init__(self, pos_x, pos_y, width, height, color, obj_id=None):
        super(Attack, self).__init__()
        self.obj_id = obj_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = height
        self.width = width
        self.color = color
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((color))
        self.rect = self.image.get_rect(bottomleft=((self.pos_x, self.pos_y)))

    def update(self, pos_x, pos_y):
        self.rect.x = pos_x
        self.pos_x = pos_x
        self.rect.y = pos_y
        self.pos_y = pos_y


class ClientFSM:
    def __init__(self):
        self.logged_in = False
        self.username_entered = False
        self.chatting = False
        self.message = ""
        self.NOTTYPING = UIText(0, screen.screen_y - 2, "PRESS ENTER TO TYPE", (255, 0, 25), "not_type")
        self.username = None
        self.password = None
        self.map_loaded = False
        self.loading = None
        self.loginimage = UIPicture((screen.screen_x / 2), (screen.screen_y / 2), 'resources/LoginBox.png')
        self.logintext = UIText(screen.screen_x / 2 - 74, screen.screen_y / 2 - 5, "", (0, 0, 0), "UI")
        self.passwordtext = UIText(screen.screen_x / 2 - 74, screen.screen_y / 2 + 43, "", (0, 0, 0), "UI")

    def update_chatting(self):
        self.chatting = not self.chatting

    def chat_logic_router(self, message=""):
        if not self.username_entered:
            self.username_handler(message)
        if not self.logged_in and self.username_entered:
            self.password_handler(message)
        else:
            if self.chatting:
                self.chatmsg_handler(message)

    def username_handler(self, message):
        while len(self.message) > 14:
            self.message = self.message[:-1]
        self.message += message
        self.logintext.update(self.message)

    def password_handler(self, message):
        while len(self.message) > 15:
            self.message = self.message[:-1]
        self.message += message
        self.passwordtext.update(self.message)

    def chatmsg_handler(self, message):
        while len(self.message) > 100:
            self.message = self.message[:-1]
        self.message += message
        messagetext.update(self.message, 250)

    def authenticate(self, message):
        try:
            message = json.loads(message)
            self.logged_in = True
            game.make_hero(75, 50, 15, 30, ((random.randint(0, 200)), (random.randint(0, 200)),
                                            (random.randint(0, 200))), message[0], message[1])
            client.sendData("INIT" + json.dumps(game.hero.object_dict))

        except:
            self.logged_in = False
            self.username = None
            self.password = None
            self.username_entered = False
            self.loading.kill()
            self.loginimage = UIPicture((screen.screen_x / 2), (screen.screen_y / 2), 'LoginBox.png')
            self.logintext = UIText(screen.screen_x / 2 - 74, screen.screen_y / 2 - 5, "", (0, 0, 0), "UI")
            self.passwordtext = UIText(screen.screen_x / 2 - 74, screen.screen_y / 2 + 43, "", (0, 0, 0), "UI")

    def enter(self):
        if self.logged_in:
            if self.chatting:
                if len(self.message) > 0:
                    client.sendData("^^" + chatclass.username + ": " + self.message)
                    self.message = ""
                    messagetext.update("")
                self.NOTTYPING = UIText(0, screen.screen_y - 2, "PRESS ENTER TO TYPE", (255, 0, 25), "not_type")
                self.update_chatting()
            else:
                self.update_chatting()
                try:
                    self.NOTTYPING.kill()
                except:
                    pass
        elif self.username_entered and not self.logged_in:
            self.logged_in = True
            self.password = self.message
            self.message = ""

            authtuple = [self.username, self.password]
            authtuple = ("^id^" + json.dumps(authtuple))
            client.sendData(authtuple)

            self.loginimage.kill()
            self.logintext.kill()
            self.passwordtext.kill()

            self.loading = UIPicture((screen.screen_x / 2), (screen.screen_y / 2), 'resources/loading_screen.jpg', True)

            #

            # game.hero = ClientHero(75, 50, 15, 30, ((random.randint(0, 200)), (random.randint(0, 200)),
                                                      # (random.randint(0, 200))), self.username)
            # client.sendData("INIT" + json.dumps(game.hero.object_dict))
            # Moved to self.map_loaded()

        elif not self.username_entered and len(self.message) > 2:
            self.username_entered = True
            self.username = self.message
            chatclass.username = self.message
            self.message = ""


class ActionFSM:
    def __init__(self):
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.action1 = False
        self.action2 = False
        self.action3 = False

    def update(self, event=None, keys=None, mods=None,  chatting=False):
        if event.type == KEYDOWN:
            if mods & KMOD_SHIFT and not self.action1:
                self.action1 = True
                client.sendData("*^A1T")
            if keys[K_w] and not self.up:
                self.up = True
                client.sendData("*^UT")
            elif keys[K_s] and not self.down:
                self.down = True
                client.sendData("*^DT")
            elif keys[K_a] and not self.left:
                self.left = True
                client.sendData("*^LT")
            elif keys[K_d] and not self.right:
                self.right = True
                client.sendData("*^RT")
        if event.type == KEYUP:
            if not mods & KMOD_SHIFT and self.action1:
                self.action1 = False
                client.sendData("*^A1F")
            if event.key == pygame.K_w and self.up:
                self.up = False
                client.sendData("*^UF")
            elif event.key == pygame.K_s and self.down:
                self.down = False
                client.sendData("*^DF")
            elif event.key == pygame.K_a and self.left:
                self.left = False
                client.sendData("*^LF")
            elif event.key == pygame.K_d and self.right:
                self.right = False
                client.sendData("*^RF")

    def stop(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        client.sendData("*^UF")
        client.sendData("*^DF")
        client.sendData("*^LF")
        client.sendData("*^RF")


class ObjectIdentity:
    def __init__(self):
        self.objects = {}
        self.object_dict = {}
        self.known_objects = []

    def identify(self, o):
        self.objects[o.obj_id] = o
        self.object_dict[o.obj_id] = {"pos_x": o.pos_x, "pos_y": o.pos_y, "width": o.width, "height": o.height,
                                         "color": o.color, "obj_id": o.obj_id}

# Initialize PyGame
pygame.init()


# Screen Settings
class Screen:
    def __init__(self):
        self.screen_x = 1200
        self.screen_y = 700
        self.screen = (self.screen_x, self.screen_y)
        self.screen = pygame.display.set_mode(self.screen)

screen = Screen()
controls = {
    "up" : K_w,
    "down": K_s,
    "left": K_a,
    "right": K_d,
    "button1": K_1,
    "button2": K_SPACE,
    "button3": K_3,
}



class Map:
    def __init__(self):
        self.map = []
        self.complete = False

    def update(self, line):
        if line == "END":
            self.map_maker(self.map)
            self.complete = True

        else:
            self.map.append(line)

    def map_maker(self, map):
        x = y = 0
        for row in map:
            for col in row:
                Tile(x, y, col)
                x += 50
            x = 0
            y += 50
        chatfsm.map_loaded = True
        chatfsm.loading.kill()

clientmap = Map()


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l + int(screen.screen_x / 2), -t + int(screen.screen_y / 2), w, h)

camera = Camera(simple_camera, 5000, 5000)

#Start Game() class
game = Game()

# Groups
nocollide = pygame.sprite.Group()
collide = pygame.sprite.Group()
tiles = pygame.sprite.Group()
ui_elements = pygame.sprite.Group()
ui_text = pygame.sprite.Group()
ui_pictures = pygame.sprite.Group()
heroes = pygame.sprite.Group()
remote_heroes = pygame.sprite.Group()
chat = pygame.sprite.Group()
loading_images = pygame.sprite.Group()
nameplates = pygame.sprite.Group()
not_type = pygame.sprite.Group()
live_chat = pygame.sprite.Group()
attk_objects = pygame.sprite.Group()



# Initialize PyGame's key_repeat
pygame.key.set_repeat(500, 30)

# Object ID Handler
identifier = ObjectIdentity()

# Create the client
client = Client()
chatclass = Chat()
chatfsm = ClientFSM()
actionfsm = ActionFSM()

# Title
pygame.display.set_caption("Pyablo II: Nord of Construction")

# UI Initialization      (pos_x, pos_y, width, height, (co, lo, r))
# THIS CAN BE CLEANED UP
chatboxlower = UIElement(0, screen.screen_y + 00, 250, 18, (66, 66, 66))
chatboxupper = UIElement(0, screen.screen_y - 18, 250, 450, (117, 117, 117))
# loginimage = UIPicture((screen.screen_x / 2), (screen.screen_y / 2), 'LoginBox.png')
messagetext = UIText(0, screen.screen_y, "", (255, 255, 255), "live_chat")
# logintext = UIText(screen.screen_x / 2 - 74, screen.screen_y / 2 - 5, "", (0, 0, 0), "UI")
# passwordtext = UIText(screen.screen_x / 2 - 74, screen.screen_y / 2 + 43, "", (0, 0, 0), "UI")

# Clock
clock = pygame.time.Clock()

# Background
background = pygame.image.load('resources/background.jpg')
background = background.convert()

# Let's GO!
running = True

client_listen_thread = threading.Thread(target=client.recvData)
client_listen_thread.daemon = True
client_listen_thread.start()



while running:
    clock.tick(60)
    screen.screen.fill(Color(0, 0, 0))
    pygame.event.pump()
    mouse_coordinates = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    mods = pygame.key.get_mods()
    for event in pygame.event.get():
        if event.type == QUIT or keys[K_ESCAPE]:
            running = False
        if event.type == KEYDOWN:
            if keys[K_RETURN]:
                chatfsm.enter()
                break
            if keys[K_TAB]:
                    break
            if chatfsm.chatting or not chatfsm.logged_in:
                if keys[K_BACKSPACE]:
                    chatfsm.message = chatfsm.message[:-1]
                    chatfsm.chat_logic_router()
                else:
                    chatfsm.chat_logic_router(str(event.unicode))
                    pygame.event.clear()
            else:  # This will move to the ActionFSM
                if keys[K_PAGEUP]:
                    chatclass.modifier_change(1)
                    chatclass.update("placeholder")
                elif keys[K_PAGEDOWN]:
                    chatclass.modifier_change(-1)
                    chatclass.update("placeholder")
                else:
                    if chatfsm.map_loaded:
                        game.hero.actionfsm(event, keys, mods)
        elif event.type == KEYUP and chatfsm.logged_in:
            if not chatfsm.chatting and chatfsm.map_loaded:
                game.hero.actionfsm(event, keys, mods)

    if chatfsm.map_loaded:
        game.hero.update()
        camera.update(game.hero)
        screen.screen.blit(background, (-1000, -1000))
        # screen.screen.blit(entity.image, camera.apply(entity)) * new method
        # screen.screen.blit(entity.image, entity.rect) *how it used to b
    for entity in tiles:
        screen.screen.blit(entity.image, camera.apply(entity))
    for entity in ui_pictures:
        screen.screen.blit(entity.image, entity.rect)
    for entity in ui_text:
        screen.screen.blit(entity.image, entity.rect)
    for entity in heroes:
        screen.screen.blit(entity.image, camera.apply(entity))
        try:
            entity.anim.play()
            # entity.anim.blit(screen.screen, entity.rect)
            entity.anim.blit(screen.screen, camera.apply(entity))
        except:
            pass
    for entity in attk_objects:
        entity.update()
        screen.screen.blit(entity.image, camera.apply(entity))
    for entity in nameplates:
        screen.screen.blit(entity.image, camera.apply(entity))
    for entity in loading_images:
        screen.screen.blit(entity.image, entity.rect)
    for entity in ui_elements:
        screen.screen.blit(entity.image, entity.rect)
    for entity in not_type:
        screen.screen.blit(entity.image, entity.rect)
    for entity in chat:
        screen.screen.blit(entity.image, entity.rect)
    for entity in live_chat:
        screen.screen.blit(entity.image, entity.rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
