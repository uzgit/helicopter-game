#!/usr/bin/env python3

import os
import math
import sys
import argparse
import importlib
import numpy

import pygame
import pygame.freetype
from pygame.constants import K_w, K_s, K_q, K_p, K_v
from lib.pygamewrapper import PyGameWrapper
from lib.vec2d import vec2d

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", help = "In <flappy> mode, an up action is like one flap of a birds wings. Pressing up gives the helicopter a momentary lift. In <helicopter> mode, an up action is like throttling up. It gives the helicopter continuous lift.", default="flappy")
parser.add_argument("-s", "--fps",     help = "Frames per second. Increase this value to go faster, decrease to go slower.", default = 30, type = float)
parser.add_argument("-a", "--agent",   help = "Name of the type of agent to use to play the game. This should be equal to the name of the agent's python file, without the '.py'", default =None, type = str)
parser.add_argument("-n", "--noisy-sensors",   help = "Adds gausian noise into the simulated sensor values. Noise amplitude for obstaces is directly proportional to the distance from the obstacle.", action="store_true")
parser.add_argument("-d", "--no-data", help = "Suppresses on-screen data output.", action="store_true")
parser.add_argument("-q", "--quiet-mode",   help = "Quiet mode simulates the game without animation.", action="store_true")
parser.add_argument("-o", "--headless",   help = "Run the game entirely without a monitor.", action="store_true")
arguments = parser.parse_args()

#emulation_speed = arguments.speed
agent_argument = arguments.agent

if agent_argument is not None:

    Agent = importlib.import_module("agents." + agent_argument)

print(arguments)

BLACK      = (  0,   0,   0)
GREY       = (169, 169, 169)
SILVER     = (192, 192, 192)
WHITE      = (255, 255, 255)
LSU_PURPLE = ( 70,  29, 124)
LSU_GOLD   = (253, 208,  35)
GREEN      = (  0, 255,  51)

WINDOW_WIDTH  = 700
WINDOW_HEIGHT = 700
BLOCK_WIDTH_COEFFICIENT   = 0.05 #default is 0.1
BLOCK_HEIGHT_COEFFICIENT  = 0.10 #default is 0.2
PLAYER_WIDTH_COEFFICIENT  = 0.03 #default = 0.05
PLAYER_HEIGHT_COEFFICIENT = 0.03 #default = 0.05

# Class for the blocks that appear in the way of the helicopter
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

# Class for the pixhel that takes the place of the helicopter
class HelicopterPlayer(pygame.sprite.Sprite):

    def __init__(self, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        helicopter = pygame.image.load("images/helicopter_tiny.png")

        pos_init = (int(SCREEN_WIDTH * 0.35), SCREEN_HEIGHT / 2)
        self.pos = vec2d(pos_init)
        self.speed = speed

        if arguments.mode == "flappy":
            self.climb_speed = speed * -0.875  # -0.0175
            self.fall_speed = speed * 0.09  # 0.0019
        else:
            self.climb_speed = speed * -0.09
            self.fall_speed = speed * 0.09

        self.momentum = 0

        self.width = SCREEN_WIDTH * PLAYER_WIDTH_COEFFICIENT
        self.height = SCREEN_HEIGHT * PLAYER_HEIGHT_COEFFICIENT

        image = pygame.Surface((2*self.width, 1.5*self.height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

#        pygame.draw.rect(
#            image,
#            WHITE,
#            (0, 0, self.width, self.height),
#            0
#        )

        image.blit(helicopter, (0,0))
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, is_climbing, dt):
        self.momentum += (self.climb_speed if is_climbing else self.fall_speed) * dt
        self.momentum *= 0.99
        self.pos.y += self.momentum

        self.rect.center = (self.pos.x, self.pos.y)

# Class for the terrain forming the border of the "cave"
class Terrain(pygame.sprite.Sprite):

    def __init__(self, pos_init, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.speed = speed
        self.width = int( SCREEN_WIDTH * 0.1) #default = 0.2

        image = pygame.Surface((self.width, SCREEN_HEIGHT * 1.5))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        color = (120, 240, 80)

        # top rect
        pygame.draw.rect(
            image,
            (WHITE),
            (0, 0, self.width, SCREEN_HEIGHT * 0.5),
            0
        )

        # bot rect
        pygame.draw.rect(
            image,
            (WHITE),
            (0, SCREEN_HEIGHT * 1.05, self.width, SCREEN_HEIGHT * 0.5),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):
        self.pos.x -= self.speed * dt
        self.rect.center = (self.pos.x, self.pos.y)

# Class for the actual Pixelcopter game object
class Pixelcopter(PyGameWrapper):
    """
    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    """

    def __init__(self, width=48, height=48, agent=None):
        actions ={
            "up"    : K_w,
            "quit"  : K_q,
            "pause" : K_p,
            "toggle_quiet_mode" : K_v
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)

        self.is_climbing = False
        self.speed = 0.0004 * width
        self.paused = False

        self.agent = agent

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
                elif key == self.actions['pause']:
                    self.paused = not self.paused

    def _handle_player_events_helicopter_mode(self):
        self.is_climbing = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == self.actions['quit']:
                    pygame.quit()
                    sys.exit()
                elif key == self.actions['pause']:
                    self.paused = not self.paused

        keystate = pygame.key.get_pressed()
        if keystate[self.actions['up']]:
            self.is_climbing = True

    def _handle_agent_action(self, action):

        self.is_climbing = False

        if   action == "up" :
            self.is_climbing = True
        elif action == "quit" :
            print("Quit requested by agent.")
            pygame.quit()
            sys.exit()
    
    def _handle_player_pause_quit_events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == self.actions['quit']:
                    pygame.quit()
                    sys.exit()
                elif key == self.actions['pause']:
                    self.paused = not self.paused
                elif key == self.actions['toggle_quiet_mode']:
                    arguments.quiet_mode = not arguments.quiet_mode

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player distance traveled
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

        scanner_height = 500 #pixels or something
        num_segments = 5
        segments = []
        for i in range(num_segments - 1):
            segment_bottom = (self.player.pos.y - scanner_height/2.0) + float(i) / num_segments * scanner_height
            segment_top = (self.player.pos.y - scanner_height/2.0) + float(i+1) / num_segments * scanner_height
            
            segment_occupied = 0.0
            if (min_block.pos.y <= segment_top and min_block.pos.y >= segment_bottom):
                segment_occupied = 1.0
            elif ((min_block.pos.y + min_block.height) <= segment_top and (min_block.pos.y + min_block.height) >= segment_bottom):
                segment_occupied = 1.0
            segments.append(segment_occupied)

        look_ahead = 3 # number of terrains (in front of copter) to get dist_to_ceil and dist_to_floor
        current_terrain_index = list(self.terrain_group).index(current_terrain)
        all_terrains = list(self.terrain_group)
        next_terrain_y_positions = []
        for i in range(look_ahead):
            next_terrain_y_positions.append(all_terrains[current_terrain_index + i].pos.y)

        #print(next_terrain_y_positions)

        height_ratios = []
        for terrain_y_position in next_terrain_y_positions:
            distance_to_ceiling = self.player.pos.y - (terrain_y_position - self.height * 0.25)
            distance_to_floor   = (terrain_y_position + self.height * 0.25) - self.player.pos.y
            height_ratios.append( distance_to_floor / (distance_to_floor + distance_to_ceiling) )

        state = {
            "distance_traveled" : self.distance_traveled,
            "player_y" : self.player.pos.y,
            "player_vel" : self.player.momentum,
            "player_dist_to_ceil" : self.player.pos.y - (current_terrain.pos.y - self.height * 0.25),
            "player_dist_to_floor" : (current_terrain.pos.y + self.height * 0.25) - self.player.pos.y,
            "next_gate_dist_to_player": min_dist,
            "next_gate_block_top" : min_block.pos.y,
            "next_gate_block_bottom" : min_block.pos.y + min_block.height,
            "height_ratios" : height_ratios,
            "segments" : segments
        }

        return state

    # Distance traveled is always given as a true value.
    def getNoisyGameState(self):

        true_state = self.getGameState()
        noisy_state = true_state.copy()

        gate_distance = true_state["next_gate_dist_to_player"]

        #numpy.random.normal( <mean> , <standard deviation> )
        noisy_state["player_y"]                 += numpy.random.normal(0, 2)
        noisy_state["player_vel"]               += numpy.random.normal(0, 0.2)
        noisy_state["player_dist_to_ceil"]  += numpy.random.normal(0, 2)
        noisy_state["player_dist_to_floor"]     += numpy.random.normal(0, 2)
        noisy_state["next_gate_block_top"]      += numpy.random.normal(0, 2 + (gate_distance / 60))
        noisy_state["next_gate_block_bottom"]   += numpy.random.normal(0, 2 + (gate_distance / 60))
        noisy_state["next_gate_dist_to_player"] += numpy.random.normal(0, 2)

        return noisy_state

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

        self.distance_traveled = 0

    def _add_terrain(self, start, end):
        w = int(self.width * 0.1) #default is 0.1
        # each block takes up 10 units.
        steps = range(start + int(w / 2), end + int(w / 2), w)
        #steps = range(start, end + w, 5)
        y_jitter = []

        freq = 4.5 / self.width + self.rng.uniform(-0.01, 0.01)
        for step in steps:
            jitter = 0.5 * (self.height * 0.125) * math.sin(freq * step + self.rng.uniform(0.0, 0.5))
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
        
        if agent is not None:
            if arguments.noisy_sensors:
                result = agent.reset(game.getNoisyGameState())
            else:
                result = agent.reset(game.getGameState())

        if result is "quit":
            print("Quit requested by agent.")
            pygame.quit()
            sys.exit()

        self.init()

    def step(self, dt):

        self.screen.fill((BLACK))

        #If the player is human
        if agent == None:
            if arguments.mode == "flappy":
                self._handle_player_events_flappy_mode()
            else:
                self._handle_player_events_helicopter_mode()

        #If the player is an agent
        else:
            if arguments.noisy_sensors:
                state = game.getNoisyGameState()
            else:
                state = game.getGameState()
            
            if agent is not None:
                agent_action = agent.get_action(state)
                game._handle_agent_action(agent_action)
                game._handle_player_pause_quit_events()


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

        if not arguments.quiet_mode:
            self.player_group.draw(self.screen)
            self.block_group.draw(self.screen)
            self.terrain_group.draw(self.screen)

        self.distance_traveled += self.speed * dt

#################################################################################################
# Some functions to display data to the screen
def display_status_line_1(status):
    return "player: (distance: %-7.2f, y position: %4.2f, y velocity: %4.2f)" % (status["distance_traveled"], status["player_y"], status["player_vel"])
def display_status_line_2(status):
    return "distance to: (ceiling: %-3.2f, floor: %3.2f)" %(status["player_dist_to_ceil"], status["player_dist_to_floor"])
def display_status_line_3(status):
    return "obstacle: (distance: %3.2f, top: %3.2f, bottom: %3.2f)" %(status["next_gate_dist_to_player"], status["next_gate_block_top"], status["next_gate_block_bottom"])

#################################################################################################
if __name__ == "__main__":
    import numpy as np

    #Instantiate the agent, if an agent is specified
    if agent_argument is not None:
        agent = Agent.Agent()
    else:
        agent = None

    #Instantiate and initialize the game
    if arguments.headless == True:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    
    pygame.init()
    game = Pixelcopter(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, agent=agent)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    #Instantiate the font used to display text on the screen
    courier_font = pygame.freetype.Font("fonts/courier.ttf", 16)

    while True:
        if game.game_over():
            game.reset()

        if not game.paused: 
            
            # Increment the time, delaying frames to keep a constant framerate
            dt = game.clock.tick_busy_loop(arguments.fps) #default is 30
            # Instead of using a dynamic dt, use a constant dt so that an agent's speed
            #   does not change relative to the game speed.
            #game.step(dt)
            game.step(33)

            # Determine whether to display data to the screen (chosen by user)
            if not arguments.no_data:

                # Choose between display noisy data or true data
                if arguments.noisy_sensors:
                    state = game.getNoisyGameState()
                else:
                    state = game.getGameState()
                
                # Display data to the screen
                courier_font.render_to(game.screen, (0,  0), display_status_line_1(state), BLACK)
                courier_font.render_to(game.screen, (0, 20), display_status_line_2(state), BLACK)
                courier_font.render_to(game.screen, (0, 40), display_status_line_3(state), BLACK)
            
            # Animate
            if not arguments.quiet_mode:
                pygame.display.update()
 
        # If the game is paused, we still need to handle a user's "quit" action.
        if game.paused:
            game._handle_player_pause_quit_events()
