#!/usr/bin/env python3

import math
import sys

#import .base

from pygamewrapper import PyGameWrapper

import pygame
import pygame.freetype
from pygame.constants import K_w, K_s, K_q
from vec2d import vec2d

BLACK      = (  0,   0,   0)
GREY       = (169, 169, 169)
SILVER     = (192, 192, 192)
WHITE      = (255, 255, 255)
LSU_PURPLE = ( 70,  29, 124)
LSU_GOLD   = (253, 208,  35)
GREEN      = (  0, 255,  51)

DISPLAY_UPDATE = '-silent' not in sys.argv and '-s' not in sys.argv

WINDOW_WIDTH  = 700
WINDOW_HEIGHT = 700
BLOCK_WIDTH_COEFFICIENT   = 0.05 #default is 0.1
BLOCK_HEIGHT_COEFFICIENT  = 0.10 #default is 0.2
PLAYER_WIDTH_COEFFICIENT  = 0.03 #default = 0.05
PLAYER_HEIGHT_COEFFICIENT = 0.03 #default = 0.05

class Block(pygame.sprite.Sprite):

    def __init__(self, pos_init, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)

        self.width = int(SCREEN_WIDTH * BLOCK_WIDTH_COEFFICIENT)
        self.height = int(SCREEN_HEIGHT * BLOCK_HEIGHT_COEFFICIENT)
        self.speed = speed

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        image = pygame.Surface((self.width, self.height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            GREY,
            (0, 0, self.width, self.height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):
        self.pos.x -= self.speed * dt

        self.rect.center = (self.pos.x, self.pos.y)


class HelicopterPlayer(pygame.sprite.Sprite):

    def __init__(self, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        pos_init = (int(SCREEN_WIDTH * 0.35), SCREEN_HEIGHT / 2)
        self.pos = vec2d(pos_init)
        self.speed = speed
        self.climb_speed = speed * -0.875  # -0.0175
        self.fall_speed = speed * 0.09  # 0.0019
        self.momentum = 0

        self.width = SCREEN_WIDTH * PLAYER_WIDTH_COEFFICIENT
        self.height = SCREEN_HEIGHT * PLAYER_HEIGHT_COEFFICIENT

        image = pygame.Surface((self.width, self.height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            WHITE,
            (0, 0, self.width, self.height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, is_climbing, dt):
        self.momentum += (self.climb_speed if is_climbing else self.fall_speed) * dt
        self.momentum *= 0.99
        self.pos.y += self.momentum

        self.rect.center = (self.pos.x, self.pos.y)


class Terrain(pygame.sprite.Sprite):

    def __init__(self, pos_init, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.speed = speed
#        self.width = int( SCREEN_WIDTH * 0.2)
        self.width = int( SCREEN_WIDTH * 0.1)

        image = pygame.Surface((self.width, SCREEN_HEIGHT * 1.5))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        color = (120, 240, 80)

        # top rect
        pygame.draw.rect(
            image,
            GREEN,
            (0, 0, self.width, SCREEN_HEIGHT * 0.5),
            0
        )

        # bot rect
        pygame.draw.rect(
            image,
            GREEN,
            (0, SCREEN_HEIGHT * 1.05, self.width, SCREEN_HEIGHT * 0.5),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):
        self.pos.x -= self.speed * dt
        self.rect.center = (self.pos.x, self.pos.y)


class Pixelcopter(PyGameWrapper):
    """
    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    """

    def __init__(self, width=48, height=48):
        actions ={
            "up"   : K_w,
            "quit" : K_q
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)

        self.is_climbing = False
        self.speed = 0.0004 * width

    def _handle_player_events_flappy_mode(self):
        self.is_climbing = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                if   key == self.actions['up']:
                    self.is_climbing = True
                elif key == self.actions['quit']:
                    pygame.quit()
                    sys.exit()

    def _handle_player_events_helicopter_mode(self):
        self.is_climbing = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keystate = pygame.key.get_pressed()
        if keystate[self.actions['up']]:
            self.is_climbing = True
        elif keystate[self.actions['quit']]:
            pygame.quit()
            sys.exit()

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player y position.
            * player velocity.
            * player distance to floor.
            * player distance to ceiling.
            * next block x distance to player.
            * next blocks top y location,
            * next blocks bottom y location.

            See code for structure.

        """

        min_dist = 999
        min_block = None
        for b in self.block_group:  # Groups do not return in order
            dist_to = b.pos.x - self.player.pos.x
            if dist_to > 0 and dist_to < min_dist:
                min_block = b
                min_dist = dist_to

        current_terrain = pygame.sprite.spritecollide(
            self.player, self.terrain_group, False)[0]
        state = {
            "player_x": self.player.pos.x,
            "player_y": self.player.pos.y,
            "player_vel": self.player.momentum,
            "player_dist_to_ceil": self.player.pos.y - (current_terrain.pos.y - self.height * 0.25),
            "player_dist_to_floor": (current_terrain.pos.y + self.height * 0.25) - self.player.pos.y,
            "next_gate_dist_to_player": min_dist,
            "next_gate_block_top": min_block.pos.y,
            "next_gate_block_bottom": min_block.pos.y + min_block.height
        }

        return state

    def getScreenDims(self):
        return self.screen_dim

    def getActions(self):
        return self.actions.values()

    def getScore(self):
        return self.score

    def game_over(self):
        return self.lives <= 0.0

    def init(self):
        self.score = 0.0
        self.lives = 1.0

        self.player = HelicopterPlayer(
            self.speed,
            self.width,
            self.height
        )

        self.player_group = pygame.sprite.Group()
        self.player_group.add(self.player)

        self.block_group = pygame.sprite.Group()
        self._add_blocks()

        self.terrain_group = pygame.sprite.Group()
        self._add_terrain(0, self.width * 4)

    def _add_terrain(self, start, end):
        w = int(self.width * 0.1) #default is 0.1
        # each block takes up 10 units.
        steps = range(start + int(w / 2), end + 10000 + int(w / 2), w)
        y_jitter = []

        freq = 4.5 / self.width + self.rng.uniform(-0.01, 0.01)
        for step in steps:
            jitter = (self.height * 0.125) * \
                math.sin(freq * step + self.rng.uniform(0.0, 0.5))
            y_jitter.append(jitter)

        y_pos = [int((self.height / 2.0) + y_jit) for y_jit in y_jitter]

        for i in range(0, len(steps)):
            self.terrain_group.add(Terrain(
                (steps[i], y_pos[i]),
                self.speed,
                self.width,
                self.height
            )
            )

    def _add_blocks(self):
        x_pos = self.rng.randint(self.width, int(self.width * 1.5))
        y_pos = self.rng.randint(
            int(self.height * 0.25),
            int(self.height * 0.75)
        )
        self.block_group.add(
            Block(
                (x_pos, y_pos),
                self.speed,
                self.width,
                self.height
            )
        )

    def reset(self):
        self.init()

    def step(self, dt):

        self.screen.fill(BLACK)
        self._handle_player_events_flappy_mode()
#        self._handle_player_events_helicopter_mode()

        self.score += self.rewards["tick"]

        self.player.update(self.is_climbing, dt)
        self.block_group.update(dt)
        self.terrain_group.update(dt)

        hits = pygame.sprite.spritecollide(
            self.player, self.block_group, False)
        for creep in hits:
            self.lives -= 1

        hits = pygame.sprite.spritecollide(
            self.player, self.terrain_group, False)
        for t in hits:
            if self.player.pos.y - self.player.height <= t.pos.y - self.height * 0.25:
                self.lives -= 1

            if self.player.pos.y >= t.pos.y + self.height * 0.25:
                self.lives -= 1

        for b in self.block_group:
            if b.pos.x <= self.player.pos.x and len(self.block_group) == 1:
                self.score += self.rewards["positive"]
                self._add_blocks()

            if b.pos.x <= -b.width:
                b.kill()

        for t in self.terrain_group:
            if t.pos.x <= -t.width:
                self.score += self.rewards["positive"]
                t.kill()

        if self.player.pos.y < self.height * 0.125:  # its above
            self.lives -= 1

        if self.player.pos.y > self.height * 0.875:  # its below the lowest possible block
            self.lives -= 1

        if len(self.terrain_group) <= (
                10 + 3):  # 10% per terrain, offset of ~2 with 1 extra
            self._add_terrain(self.width, self.width * 5)

        if self.lives <= 0.0:
            self.score += self.rewards["loss"]

        self.player_group.draw(self.screen)
        self.block_group.draw(self.screen)
        self.terrain_group.draw(self.screen)

def display_status_line_1(status):

    return "player:    (x position: %5.2f, y position: %3.2f, y velocity: %3.2f)" % (status["player_x"], status["player_y"], status["player_vel"])

def display_status_line_2(status):

    return "distance to: (ceiling: %3.2f, floor: %3.2f)" %(status["player_dist_to_ceil"], status["player_dist_to_floor"])

            #"next_gate_dist_to_player": min_dist,
            #"next_gate_block_top": min_block.pos.y,
            #"next_gate_block_bottom": min_block.pos.y + min_block.height

def display_status_line_3(status):

    return "obstacle: (distance: %3.2f, top: %3.2f, bottom: %3.2f)" %(status["next_gate_dist_to_player"], status["next_gate_block_top"], status["next_gate_block_bottom"])

if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = Pixelcopter(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()
    courier_font = pygame.freetype.Font("courier.ttf", 16)

    while True:
        if game.game_over():
            game.reset()
        dt = game.clock.tick_busy_loop(30)
        game.step(dt)
        pygame.display.update()

        state = game.getGameState()
        courier_font.render_to(game.screen, (0,  0), display_status_line_1(state), BLACK)
        courier_font.render_to(game.screen, (0, 20), display_status_line_2(state), BLACK)
        courier_font.render_to(game.screen, (0, 40), display_status_line_3(state), BLACK)

        pygame.display.flip()
