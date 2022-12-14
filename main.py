import pygame
import re
from pygame.locals import *
import numpy as np
import math

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
PLAYER_SIZE = 60
BACKGROUND = (0, 0, 0)
TILE_SIZE = 64
vec = pygame.math.Vector2
image = pygame.image.load('assets/cube.png')
ship_image = pygame.image.load('assets/ship0.png')
wave_image = pygame.image.load('assets/wave.png')
cube_portal_1 = pygame.image.load('assets/portal0.png')
cube_portal_2 = pygame.image.load('assets/portal1.png')
ship_portal_1 = pygame.image.load('assets/portal2.png')
ship_portal_2 = pygame.image.load('assets/portal3.png')
w, h = image.get_size()
sw, sh = ship_image.get_size()
ww, wh = wave_image.get_size()
level_speed = 10
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image2, start_x, start_y):
        super().__init__()

        self.image = pygame.image.load(image2)
        self.rect = self.image.get_rect()

        self.rect.bottomleft = [start_x, start_y]

class Obstacle(Sprite):
    def __init__(self, file, start_x, start_y):
        super().__init__(file, start_x, start_y)

    def draw(self):
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def update(self):
        hsp = -level_speed  # horizontal speed
        self.move(hsp, 0)

class Portal(Sprite):
    def __init__(self, file, start_x, start_y):
        super().__init__(file, start_x, start_y)

    def draw(self):
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def update(self):
        hsp = -level_speed  # horizontal speed
        self.move(hsp, 0)

class Player(Sprite):
    def __init__(self, starting_image, start_x, start_y):
        super().__init__(starting_image, start_x, start_y)
        self.speed = 4 # Randomly chosen to get physics as close as possible
        self.jumpspeed = 22
        self.gravity = 1.5
        self.vsp = 0  # vertical speed
        self.rotated_rectangle = self.rect
        self.rotated_image = self.image

        self.angle = 0
        self.game_mode = "cube"
        self.alive = 1
        self.flight = 0.5

        self.ship = ship_image
        self.ship_rotated_rectangle = self.rect
        self.ship_rotated_image = self.image

    def draw(self):
        screen.blit(self.image, self.rect)

    def draw_ship_rotated(self):
        screen.blit(self.ship_rotated_image, self.ship_rotated_rectangle)

    def draw_rotate(self):
        screen.blit(self.rotated_image, self.rotated_rectangle)

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def update(self, ground, ceiling):
        hsp = 0   # horizontal speed
        on_ground = pygame.sprite.spritecollideany(self, ground)
        on_ceiling = pygame.sprite.spritecollideany(self, ceiling)
        # in_portal = pygame.sprite.spritecollideany(self, portals)

        # check keys
        key = pygame.key.get_pressed()

        if self.game_mode == "cube":  # cube
            if key[pygame.K_SPACE] and on_ground:
                    self.vsp = -self.jumpspeed
            if self.vsp < 10 and not on_ground:  # 9.8: rounded up
                self.vsp += self.gravity
            if self.vsp > 0 and on_ground:
                self.vsp = 0

        # if self.game_mode == "ship": # ship
        #     angle_adjustment_speed = 3.0  # I stole this value
        #     if key[pygame.K_SPACE]:
        #         self.vsp -= self.flight
        #     elif not on_ground and not key[pygame.K_SPACE] and self.vsp < 10:
        #         self.angle += angle_adjustment_speed
        #         self.vsp += self.flight
        #     elif on_ground:
        #         self.vsp = 0
        #     if self.vsp < 0 and on_ceiling:
        #         self.vsp = 0
        # elif self.game_mode == "cube": # cube
        #     if key[pygame.K_SPACE] and on_ground:
        #         self.vsp = -self.jumpspeed
        #     if self.vsp < 10 and not on_ground:  # 9.8: rounded up
        #         self.vsp += self.gravity
        #     if self.vsp > 0 and on_ground:
        #         self.vsp = 0
        # elif self.game_mode == "wave":
        #     if key[pygame.K_SPACE]:
        #         self.vsp = -10
        #     elif not on_ground and not key[pygame.K_SPACE]:
        #         self.vsp = 10
        #     if self.vsp > 0 and on_ground:
        #         self.vsp = 0
        #     if self.vsp < 0 and on_ceiling:
        #         self.vsp = 0

        # else:
        #     level_speed = 10

        if self.alive:
            self.move(0, self.vsp)

class Ground(Sprite):
    def __init__(self, start_x, start_y):
        super().__init__("assets/floor2.png", start_x, start_y)

    def draw(self):
        screen.blit(self.image, self.rect)

class Background:
    def __init__(self):
        self.bg = pygame.image.load('assets/background2.png').convert()
        self.bgX = 0
        self.bgX2 = self.bg.get_width()

    def redraw_background(self):
        screen.blit(self.bg, (self.bgX, 0))  # draws our first bg image
        screen.blit(self.bg, (self.bgX2, 0))  # draws the second bg image
        if self.bgX < self.bg.get_width() * -1:  # If our bg is at the -width then reset its position
            self.bgX = self.bg.get_width()

        if self.bgX2 < self.bg.get_width() * -1:
            self.bgX2 = self.bg.get_width()

class Map:
    def __init__(self, game_map):
        self.game_map = game_map

        # self.spike_img = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        # self.spike_img.fill((128, 0, 0))
        self.spike_img = pygame.image.load('assets/spike.png')
        self.spike_img = pygame.transform.scale(self.spike_img, (TILE_SIZE, TILE_SIZE))

        # self.block_img = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        # self.block_img.fill((0, 0, 0))
        self.block_img = pygame.image.load('assets/block.png')
        self.block_img = pygame.transform.scale(self.block_img, (TILE_SIZE, TILE_SIZE))

        self.groundSpikes_img = pygame.image.load('assets/groundSpikes.png')
        self.groundSpikes_img = pygame.transform.scale(self.groundSpikes_img, (TILE_SIZE, TILE_SIZE))

        self.highHalfBlock_img = pygame.image.load('assets/highHalfBlock.png')
        self.highHalfBlock_img = pygame.transform.scale(self.highHalfBlock_img, (TILE_SIZE, TILE_SIZE))

        self.shortSpike_img = pygame.image.load('assets/shortSpike.png')
        self.shortSpike_img = pygame.transform.scale(self.shortSpike_img, (TILE_SIZE, TILE_SIZE))

        self.upsidedownSpike_img = pygame.image.load('assets/upsidedownSpike.png')
        self.upsidedownSpike_img = pygame.transform.scale(self.upsidedownSpike_img, (TILE_SIZE, TILE_SIZE))

        self.ground_img = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        self.ground_img.fill((0, 255, 0))

        self.tile_rects = []

        for y, layer in enumerate(self.game_map):
            for x, tile in enumerate(layer):
                if tile != 0:
                    self.tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw(self, offset):
        for y, layer in enumerate(self.game_map):
            for x, tile in enumerate(layer):
                if not tile == 0:
                    # screen.blit(self.block_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))
                    if tile == 2:
                        screen.blit(self.spike_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))
                    elif tile == 21 or tile == 22:
                        screen.blit(self.groundSpikes_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))
                    elif tile == 7 or tile == 20:
                        screen.blit(self.highHalfBlock_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))
                    elif tile == 3:
                        screen.blit(self.shortSpike_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))
                    elif tile == 23:
                        screen.blit(self.upsidedownSpike_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))
                    elif tile == 1 or not tile == 0:
                        screen.blit(self.block_img, (x * TILE_SIZE - offset.x, y * TILE_SIZE - offset.y))




def blitRotate(player, pos, originPos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    # screen.blit(rotated_image, rotated_image_rect)
    player.rotated_image = rotated_image
    player.rotated_rectangle = rotated_image_rect
    # draw rectangle around the image
    pygame.draw.rect(screen, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)

def blitRotateShip(player, pos, originPos, angle):
    # offset from pivot to center
    image_rect = ship_image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    if player.game_mode == "ship":
        # get a rotated image
        rotated_image = pygame.transform.rotate(ship_image, angle)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    else:
        # get a rotated image
        rotated_image = pygame.transform.rotate(wave_image, angle)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    # screen.blit(rotated_image, rotated_image_rect)
    player.ship_rotated_image = rotated_image
    player.ship_rotated_rectangle = rotated_image_rect
    # draw rectangle around the image
    pygame.draw.rect(screen, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)

def load_map_optimized(map_num):
    level_file = open('maps/' + str(map_num) + '.save', 'r')
    prop_file = open('maps/' + str(map_num) + '.prop', 'r')

    width = int(re.search(r'\d+', prop_file.readline()).group())
    height = int(re.search(r'\d+', prop_file.readline()).group())
    hue = int(re.search(r'\d+', prop_file.readline()).group())

    my_map = []
    count = 0
    flag = 0
    for w_map in range(height): # optimized method of reading in map files
        col = []
        for h_map in range(width):
            temp = int(level_file.readline())
            if temp != 0:
                flag = 1
            col.append(temp)

        if flag == 1:
            my_map.append(col)
            count = count + len(col)
            temp_count = 0
            # flag = 0
    #
    # for x_print in my_map:
    #     print(*x_print, sep='')

    return my_map

def main():

    temp_list = []
    continue_loading = 1
    current_pos = 0
    ending_pos = 0
    my_map = load_map_optimized(0)
    map_data = Map(my_map)
    count = 0

    pygame.init()
    background = Background()
    ground = Ground(0, HEIGHT + 256/2) # 256
    player = Player('assets/cube.png', screen.get_width()/3, ground.rect.top)

    ceiling = Ground(0, 0)

    platforms = pygame.sprite.Group()
    platforms.add(ground)
    top_platforms = pygame.sprite.Group()
    top_platforms.add(ceiling)

    # ship_portal_group = pygame.sprite.Group()
    # cube_portal_group = pygame.sprite.Group()
    #
    # ship_portal = Portal('assets/portal2.png', 1000, HEIGHT - 100)
    # cube_portal = Portal('assets/portal0.png', 2000, HEIGHT - 100)
    # ship_portal_group.add(ship_portal)
    # cube_portal_group.add(cube_portal)

    clock = pygame.time.Clock()
    angle = 0
    ship_angle = 0
    ship_angle_new = 0
    ship_angle_old = 0
    ship_angle_change = 0

    vertical_velocity_new = 0
    vertical_velocity_old = 0
    angle_adjust_speed = 1

    scroll = pygame.math.Vector2(0, ground.rect.top - 345) # 345

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(ground)
    running = True

    while running:
        clock.tick(60) #framerate
        background.bgX -= 1.3  # Move both background images back
        background.bgX2 -= 1.3

        background.redraw_background()
        ground.draw()
        ceiling.draw()
        # ship_portal.draw()
        # ship_portal.update()
        # #cube_portal.draw()
        # #cube_portal.update()
        #
        player.update(platforms, top_platforms)
        # in_ship_portal = pygame.sprite.spritecollideany(player, ship_portal_group)
        # in_cube_portal = pygame.sprite.spritecollideany(player, cube_portal_group)

        # if player.game_mode == "ship":
        #     player.image = ship_image
        #     if in_cube_portal:
        #         print('game mode is ship and in cube portal')
        #         # player.game_mode = "cube"
        #         ship_portal_group.remove(ship_portal)
        # elif player.game_mode == "cube":
        #     player.image = image
        #     player.image = pygame.image.load('assets/cube.png')
        #     if in_ship_portal:
        #         print('game mode is cube and in ship portal')
        #         # player.game_mode = "ship"
        #         ship_portal_group.remove(cube_portal)
        # elif player.game_mode == "wave":
        #     player.image = wave_image
        #     sw, sh = wave_image.get_size()

        pos = (player.rect.bottomleft[0] + player.rect.width / 2, player.rect.bottomleft[1] - player.rect.height / 2)

        vertical_velocity_new = player.vsp
        vertical_velocity_change = vertical_velocity_new - vertical_velocity_old

        on_ground = pygame.sprite.spritecollideany(player, platforms)
        on_ceiling = pygame.sprite.spritecollideany(player, top_platforms)

        scroll.update(scroll.x + 10, scroll.y)
        offset = pygame.math.Vector2(int(scroll.x), int(scroll.y))
        # print(offset.x, offset.y)
        map_data.draw(offset)

        if player.game_mode == "cube" and player.vsp != 0.0:
            blitRotate(player, pos, (w / 2, h / 2), angle)
            angle -= 10
            angle = angle % 360
            player.draw_rotate()
        elif player.game_mode == "cube" and player.vsp == 0:
            blitRotate(player, pos, (w / 2, h / 2), 0)
            player.draw_rotate()

        # if player.game_mode == "cube" and player.vsp != 0.0:
        #     blitRotate(player, pos, (w / 2, h / 2), angle)
        #     angle -= 10
        #     angle = angle % 360
        #     player.draw_rotate()
        # elif player.game_mode == "cube" and player.vsp == 0:
        #     blitRotate(player, pos, (w / 2, h / 2), 0)
        #     player.draw_rotate()
        # elif player.game_mode == "ship" and player.vsp >= 0.0:
        #     if ship_angle < -30:
        #         ship_angle = -30
        #     if vertical_velocity_change >= 0:
        #         ship_angle -= angle_adjust_speed
        #     else:
        #         ship_angle += angle_adjust_speed
        #     blitRotateShip(player, pos, (sw / 2, sh / 2), ship_angle)
        #     player.draw_ship_rotated()
        # elif player.game_mode == "ship" and player.vsp < 0.0:
        #     if ship_angle > 30:
        #         ship_angle = 30
        #     if vertical_velocity_change <= 0:
        #         ship_angle += angle_adjust_speed
        #     else:
        #         ship_angle -= angle_adjust_speed
        #     blitRotateShip(player, pos, (sw / 2, sh / 2), ship_angle)
        #     player.draw_ship_rotated()
        # elif player.game_mode == "wave" and player.vsp > 0.0:
        #     blitRotateShip(player, pos, (w / 2, h / 2), -45)
        #     player.draw_ship_rotated()
        # elif player.game_mode == "wave" and player.vsp < 0.0:
        #     blitRotateShip(player, pos, (ww / 2, wh / 2), 45)
        #     player.draw_ship_rotated()
        # elif player.game_mode == "wave" and player.vsp == 0.0:
        #     blitRotateShip(player, pos, (ww / 2, wh / 2), 0)
        #     player.draw_ship_rotated()
        # if (player.game_mode == "ship" or player.game_mode == "wave") and (on_ground or on_ceiling):
        #     ship_angle = 0
        #     blitRotateShip(player, pos, (sw / 2, sh / 2), ship_angle)
        #     player.draw_ship_rotated()

        vertical_velocity_old = player.vsp

        # render
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        pygame.display.update()


if __name__ == "__main__":
    main()
