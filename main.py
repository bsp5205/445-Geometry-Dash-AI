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

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, start_x, start_y):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.bottomleft = [0, start_y]

    def draw(self):
        screen.blit(self.image, self.rect)

class Player(Sprite):
    def __init__(self, start_x, start_y):
        super().__init__("assets/cube.png", start_x, start_y)
        self.speed = 4
        self.jumpspeed = 20
        self.gravity = 1.5
        self.vsp = 0  # vertical speed
        self.angle = 0

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def update(self, ground):
        hsp = 10  # horizontal speed
        on_ground = pygame.sprite.spritecollideany(self, ground)

        # check keys
        key = pygame.key.get_pressed()
        # if key[pygame.K_LEFT]:
        #     hsp = -self.speed
        # elif key[pygame.K_RIGHT]:
        #     hsp = self.speed

        if key[pygame.K_SPACE] and on_ground:
            self.vsp = -self.jumpspeed

        if self.vsp < 10 and not on_ground:  # 9.8: rounded up
            self.vsp += self.gravity

        if self.vsp > 0 and on_ground:
            self.vsp = 0

        # movement
        self.move(hsp, self.vsp)

class Ground(Sprite):
    def __init__(self, start_x, start_y):
        super().__init__("assets/floor2.png", start_x, start_y)

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

def main():
    pygame.init()
    background = Background()
    ground = Ground(0, HEIGHT + 256/2)
    player = Player(0, ground.rect.top)

    platforms = pygame.sprite.Group()
    platforms.add(ground)

    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(ground)

    running = True
    while running:
        background.redraw_background()
        background.bgX -= 1.3  # Move both background images back
        background.bgX2 -= 1.3
        player.update(platforms)

        # Draw loop
        #screen.fill(BACKGROUND)

        ground.draw()
        player.draw()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        clock.tick(60)


if __name__ == "__main__":
    main()
