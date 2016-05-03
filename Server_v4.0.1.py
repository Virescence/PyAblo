import socket
import sys
import threading
import multiprocessing
import time
import pygame
import random
import json
import levels
import socketserver

# test
class Server():
    def __init__(self):
        self.host = ""
        self.port = 1234
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.client_address_list = []
        self.id_to_object = {}
        self.id_to_dict = {}
        self.message_count = 100000

    def listen(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            print("recv data from client: " + repr(data))
            if addr not in self.client_address_list:
                self.new_connection(data, addr)
            threading.Thread(target=self.dataHandler(data, addr)).start()

        except:
            pass

    def send(self, data, addr=None):
        if addr:
            self.sock.sendto(data, addr)
        else:
            for client in self.client_address_list:
                self.sock.sendto(data, client)

    def dataHandler(self, data, addr):
        data = data.decode()
        if data[0:2] == "^^":
            self.textHandler(data[2:])
        elif data[0:4] == "^id^":
            data = json.loads(data[4:])
            self.authHandler(data, addr)
        elif data[0:4] == "^db^":
            if data[4:9] == "False":
                self.failedAuthentication(data[9:])
            else:
                self.successfulAuthentication(data[4:])
        elif data[0:2] == "*^":
            data = data[2:]
            data = json.loads(data)
            self.remoteobjectHandler(data, addr)
        elif data[0:2] == "**":
            self.clientHandler(identifier.object_dict[int(data[2:])], addr)
            
    def new_connection(self, data, addr):
        data = data.decode()
        print("line 65: " + repr(data))
        if data[:4] == "INIT":
            data = json.loads(data[4:])
            print(type(data))
            self.client_address_list.append(addr)
            print(self.client_address_list)
            print("line 70")
            Hero(data["pos_x"], data["pos_y"], data["width"], data["height"], data["color"], data["name"],
                 data["obj_id"], addr)
            print("line 73")
            for line in servermap.map:
                line = "TILE" + line
                print(line)
                self.send(line.encode(), addr)
            for key in self.id_to_dict:
                self.send(("^INIT^" + json.dumps(self.id_to_dict[key])).encode(), addr)
                print(self.id_to_dict[key])

    def authHandler(self, data, addr):
        data = json.dumps([data, addr]).encode()
        self.send(data, ("localhost", 1235))

    def failedAuthentication(self, data):
        addr = json.loads(data)
        message = "^db^False"
        self.send(message.encode(), (addr[0], addr[1]))

    def successfulAuthentication(self, data):
        data = json.loads(data)
        addr = data[2]
        print(addr)
        print(type(addr))
        data = "^db^" + json.dumps(data[:2])
        self.send(data.encode(), (addr[0], addr[1]))

    def textHandler(self, data):
        data = "^^%s^^" % str(self.message_count) + data
        self.message_count += 1
        self.send(data.encode())

    def remoteobjectHandler(self, data, addr):
        pos_x = data[0][0]
        pos_y = data[0][1]
        obj_id = data[1]
        if obj_id not in self.id_to_object:
            self.send("HeroReq", addr)
        else:
            self.id_to_object[obj_id].update(pos_x, pos_y)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Client():
    def __init__(self, addr, hero_dict):
        self.username = ""
        self.addr = addr
        self.retries = 0
        self.gameserver = gameserver
        # self.gameserver.client_list.append(self.addr)
        self.gameserver.client_dd[self.addr] = dict
        self.gameserver.client_sdd[self.addr] = {"pos_x": dict["pos_x"], "pos_y": dict["pos_y"]}

        self.gameserver.client_hero_dict[self.addr] = Hero(dict["pos_x"], dict["pos_y"], dict["width"], dict["height"],
                                                           dict["color"], dict["name"], self.gameserver, self.addr)
        self.gameserver.client_obj_dict[self.addr] = self
        self.gameserver.clientHandler(">>" + str(self.gameserver.client_dd[self.addr]["obj_id"]))

    def update(self, failed):
        if failed:
            self.retries += 1
        else:
            self.retries = 0
        if self.retries >= 5:
            self.gameserver.client_list.remove(self.addr)

    def username(self, name):
        self.username = name

class Hero(Entity):
    def __init__(self, pos_x, pos_y, width, height, color, name, obj_id, addr):
        super(Hero, self).__init__()
        print("hero init!!!")
        self.addr = addr
        self.name = name
        self.obj_id = obj_id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = height
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.moving_left = False
        self.moving_right = False
        self.grounded = False
        self.action1 = False
        self.action2 = False
        self.action3 = False
        self.change_x = 0
        self.change_y = 0
        self.width = width
        self.color = color
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((color))
        self.rect = self.image.get_rect(center=((self.pos_x, self.pos_y)))
        heroes.add(self)
        self.obj_dict_constructor()
        server.send(("^INIT^" + json.dumps(server.id_to_dict[self.obj_id])).encode())

    def obj_dict_constructor(self):
        server.id_to_dict[self.obj_id] = {"pos_x": self.pos_x, "pos_y": self.pos_y, "width": self.width,
                                          "height": self.height, "color": self.color, "name": self.name,
                                          "obj_id": self.obj_id}
        server.id_to_object[self.obj_id] = self

    def actionfsm(self, *args):
        for arg in args:
            if arg == "UT":
                self.up = True
            elif arg == "DT":
                self.down = True
            elif arg == "LT":
                self.left = True
            elif arg == "RT":
                self.right = True
            elif arg == "A1T":
                self.action1 = True
            elif arg == "A2T":
                self.action2 = True
            elif arg == "A3T":
                self.action3 = True
            elif arg == "UF":
                self.up = False
            elif arg == "DF":
                self.down = False
            elif arg == "LF":
                self.left = False
            elif arg == "RF":
                self.right = False
            elif arg == "A1F":
                self.action1 = False
            elif arg == "A2F":
                self.action2 = False
            elif arg == "A3F":
                self.action3 = False

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y
        server.id_to_dict[self.obj_id]["pos_x"] = self.rect.x
        server.id_to_dict[self.obj_id]["pos_y"] = self.rect.y
        server.send(("*^" + json.dumps([[self.rect.x, self.rect.y], self.obj_id])).encode())
        # self.gameserver.client_sdd[self.addr]["pos_x"] = self.rect.x
        # self.gameserver.client_dd[self.addr]["pos_y"] = self.rect.y
        # self.gameserver.client_sdd[self.addr]["pos_y"] = self.rect.y
        # self.gameserver.clientHandler(self.gameserver.client_sdd[self.addr])

    def gravity(self):
        if self.grounded:
            return None
        elif self.change_y == 0:
            self.change_y = .5
        else:
            self.change_y += .5

    def health(self, dmg=None, heal=None):
        if dmg:
            self.hp += -dmg
        if heal:
            self.hp += heal

class HeroName(object):
    def __init__(self, pos_x, pos_y, text):
        super(HeroName, self).__init__()
        self.text = text
        self.pos_x = pos_x
        self.pos_y = pos_y

    def update(self, pos_x, pos_y):
        self.rect.x = pos_x
        self.rect.y = pos_y

class Object_Identity:
    def __init__(self):
        self.object_id = 0
        self.objects = {}
        self.object_dict = {}

    def identify(self, o):
        self.object_id += 1
        # self.objects[o.object_id] = o
        return self.object_id

    def obj_dict_constructor(self, o):
        self.object_dict[o.object_id] = {"pos_x": o.pos_x, "pos_y": o.pos_y, "width": o.width, "height": o.height,
                                         "color": o.color, "name": o.name, "obj_id": o.object_id}

class Tile(Entity):
    def __init__(self, pos_x, pos_y, tile):
        super(Tile, self).__init__()
        self.image = pygame.Surface([50, 50])
        self.rect = self.image.get_rect(bottomleft=((pos_x, pos_y)))
        if tile == "1":
            collide.add(self)

class ServerMap():
    def __init__(self):
        self.map_dict = {}
        self.map = None

    def map_maker(self, map):
        self.map = map
        self.map.append("END")
        x = y = 0
        tile_id = 0
        for row in map:
            for col in row:
                tile_id += 1
                Tile(x, y, col)
                d = {"pos_x": x, "pos_y": y, "tile": col}
                self.map_dict[tile_id] = d
                x += 50
            x = 0
            y += 50

def object_handler(data):
    Hero(data["pos_x"], data["pos_y"], data["width"], data["height"], data["color"], data["name"], data["obj_id"])


# Groups
heroes = pygame.sprite.Group()
collide = pygame.sprite.Group()

# Map
servermap = ServerMap()
servermap.map_maker(levels.maps(2))

# Server
server = Server()

identifier = Object_Identity()
running = True

while running:
    server.listen()

sys.exit()
