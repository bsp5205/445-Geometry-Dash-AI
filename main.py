import pygame
import re
from pygame.locals import *
import numpy as np

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
PLAYER_SIZE = 60
BACKGROUND = (0, 0, 0)
vec = pygame.math.Vector2
image = pygame.image.load('assets/cube.png')
w, h = image.get_size()

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, start_x, start_y):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.bottomleft = [0, start_y]


class Player(Sprite):
    def __init__(self, start_x, start_y):
        super().__init__("assets/cube.png", start_x, start_y)
        self.speed = 4
        self.jumpspeed = 22
        self.gravity = 1.5
        self.vsp = 0  # vertical speed
        self.jumping = 0
        self.rotated_rectangle = self.rect
        self.rotated_image = self.image
        self.angle = 0

    def draw(self):
        screen.blit(self.image, self.rect)

    def draw_rotate(self):
        screen.blit(self.rotated_image, self.rotated_rectangle)

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def update(self, ground):
        hsp = 0  # horizontal speed
        on_ground = pygame.sprite.spritecollideany(self, ground)

        # check keys
        key = pygame.key.get_pressed()
        # if key[pygame.K_LEFT]:
        #     hsp = -self.speed
        # elif key[pygame.K_RIGHT]:
        #     hsp = self.speed

        if key[pygame.K_SPACE] and on_ground:
            self.jumping = 1
            self.vsp = -self.jumpspeed

        if self.vsp < 10 and not on_ground:  # 9.8: rounded up
            self.vsp += self.gravity

        if self.vsp > 0 and on_ground:
            self.jumping = 0
            self.vsp = 0

        # movement
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
    # pygame.draw.rect(screen, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)

def main():
    pygame.init()
    background = Background()
    ground = Ground(0, HEIGHT + 256/2)
    player = Player(0, ground.rect.top)

    platforms = pygame.sprite.Group()
    platforms.add(ground)

    clock = pygame.time.Clock()
    angle = 0
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(ground)
    running = True
    while running:
        clock.tick(60)
        background.bgX -= 1.3  # Move both background images back
        background.bgX2 -= 1.3

        pos = (player.rect.bottomleft[0] + 30, player.rect.bottomleft[1] - 30)

        background.redraw_background()
        ground.draw()
        player.update(platforms)

        if player.vsp != 0.0:
            blitRotate(player, pos, (w / 2, h / 2), angle)
            angle -= 10
            angle = angle % 360
            # print(angle)
            player.draw_rotate()
        else:
            # print(player.angle)
            blitRotate(player, pos, (w / 2, h / 2), player.angle)
            player.draw_rotate()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        pygame.display.update()


if __name__ == "__main__":
    main()
