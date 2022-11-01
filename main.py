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
w, h = image.get_size()
sw, sh = ship_image.get_size()

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
        hsp = -10  # horizontal speed
        self.move(hsp, 0)


class Player(Sprite):
    def __init__(self, starting_image, start_x, start_y):
        super().__init__(starting_image, start_x, start_y)
        self.speed = 4
        self.jumpspeed = 22
        self.gravity = 1.5
        self.vsp = 0  # vertical speed
        self.jumping = 0
        self.rotated_rectangle = self.rect
        self.rotated_image = self.image

        self.angle = 0
        self.is_cube = 0
        self.alive = 1
        self.flight = 0.5

        self.ship = ship_image
        self.ship_rotated_rectangle = self.rect
        self.ship_rotated_image = self.image

    def draw(self):
        screen.blit(self.image, self.rect)

    def draw_ship_rotated(self):
        screen.blit(self.ship_rotated_image, self.rotated_rectangle)

    def draw_rotate(self):
        screen.blit(self.rotated_image, self.rotated_rectangle)

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def update(self, ground, ceiling):
        hsp = 0   # horizontal speed
        on_ground = pygame.sprite.spritecollideany(self, ground)
        on_ceiling = pygame.sprite.spritecollideany(self, ceiling)
        # check keys
        key = pygame.key.get_pressed()
        # if key[pygame.K_LEFT]:
        #     hsp = -self.speed
        # elif key[pygame.K_RIGHT]:
        #     hsp = self.speed

        if self.is_cube:
            if key[pygame.K_SPACE] and on_ground:
                self.jumping = 1
                self.vsp = -self.jumpspeed

            if self.vsp < 10 and not on_ground:  # 9.8: rounded up
                self.vsp += self.gravity

            if self.vsp > 0 and on_ground:
                self.jumping = 0
                self.vsp = 0
        else:
            angle_adjustment_speed = 3.0
            if key[pygame.K_SPACE]:
                ship_angle = 0
                self.vsp -= self.flight
            elif not on_ground and not key[pygame.K_SPACE] and self.vsp < 10:
                self.angle += angle_adjustment_speed
                self.vsp += self.flight
            elif on_ground:
                self.vsp = 0

            if self.vsp < 0 and on_ceiling:
                print('ON CEILING')
                self.jumping = 0
                self.vsp = 0

        if self.alive:
            self.move(hsp, self.vsp)

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
    #screen.blit(rotated_image, rotated_image_rect)
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

    # get a rotated image
    rotated_image = pygame.transform.rotate(ship_image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    #screen.blit(rotated_image, rotated_image_rect)
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

    # for x in my_map:
    #     print(*x, sep='')

    return my_map

def main():

    temp_list = []
    continue_loading = 1
    current_pos = 0
    ending_pos = 0
    #my_map = load_map_optimized(0)
    count = 0

    pygame.init()
    background = Background()
    ground = Ground(0, HEIGHT + 256/2)
    player = Player('assets/cube.png', 0, ground.rect.top)

    ceiling = Ground(0, 0)

    platforms = pygame.sprite.Group()
    platforms.add(ground)
    top_platforms = pygame.sprite.Group()
    top_platforms.add(ceiling)

    clock = pygame.time.Clock()
    angle = 0
    ship_angle = 0
    ship_angle_new = 0
    ship_angle_old = 0
    ship_angle_change = 0

    vertical_velocity_new = 0
    vertical_velocity_old = 0
    angle_adjust_speed = 1

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(ground)
    running = True
    while running:
        clock.tick(60) #framerate
        background.bgX -= 1.3  # Move both background images back
        background.bgX2 -= 1.3

        pos = () # ignore this

        background.redraw_background()
        ground.draw()
        ceiling.draw()
        player.update(platforms, top_platforms)

        if player.is_cube:
            pos = (player.rect.bottomleft[0] + player.rect.width/2, player.rect.bottomleft[1] - player.rect.height/2)
            player.image = pygame.image.load('assets/cube.png')
        else:
            pos = (player.rect.bottomleft[0] + player.rect.width/2, player.rect.bottomleft[1] - player.rect.height/2)

        vertical_velocity_new = player.vsp
        vertical_velocity_change = vertical_velocity_new - vertical_velocity_old

        ship_angle_new = ship_angle
        ship_angle_change = ship_angle_new - ship_angle_old

        on_ground = pygame.sprite.spritecollideany(player, platforms)
        on_ceiling = pygame.sprite.spritecollideany(player, top_platforms)
        if player.vsp != 0.0 and player.is_cube:
            blitRotate(player, pos, (w / 2, h / 2), angle)
            angle -= 10
            angle = angle % 360
            player.draw_rotate()
        elif player.vsp == 0 and player.is_cube:
            blitRotate(player, pos, (w / 2, h / 2), player.angle)
            player.draw_rotate()
        elif player.vsp > 0.0 and not player.is_cube:  # player moving down
            if ship_angle < -30:
                ship_angle = -30
            if vertical_velocity_change >= 0:
                ship_angle -= angle_adjust_speed
            else:
                ship_angle += angle_adjust_speed
            blitRotateShip(player, pos, (sw/2, sh/2), ship_angle)
            player.draw_ship_rotated()
        elif player.vsp < 0.0 and not player.is_cube: # player moving up
            if ship_angle > 30:
                ship_angle = 30
            if vertical_velocity_change <= 0:
                ship_angle += angle_adjust_speed
            else:
                ship_angle -= angle_adjust_speed
            blitRotateShip(player, pos, (sw / 2, sh / 2), ship_angle)
            player.draw_ship_rotated()
        elif not player.is_cube and on_ground or on_ceiling:
            ship_angle = 0
            blitRotateShip(player, pos, (sw / 2, sh / 2), ship_angle)
            player.draw_ship_rotated()

        vertical_velocity_old = player.vsp
        ship_angle_old = ship_angle

        # render

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        pygame.display.update()


if __name__ == "__main__":
    main()
