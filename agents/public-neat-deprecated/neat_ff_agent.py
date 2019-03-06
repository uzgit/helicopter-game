from __future__ import print_function
import os
import neat
from .population import *
import random

# Initial skeleton for agents
class Agent():

    def __init__(self, generations = 300):

        local_dir = os.path.dirname(__file__)
        config_file = os.path.join(local_dir, 'config-feedforward')

        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

        self.generations = generations

        self.population_object = Population(self.config)

        self.population_object.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.population_object.add_reporter(self.stats)
        self.population_object.add_reporter(neat.Checkpointer(5))

        self.config = self.population_object.init_run(n=self.generations)

        self.genome_index = 0
        genome_id, genome = self.population_object.get_population()[self.genome_index]
        self.current_network = neat.nn.FeedForwardNetwork.create(genome, self.config)
 
    # This is the name of the constructor used by the game.
    # Be sure to call the actual constructor here.
    def Agent(self):

        self.__init__()

    def reset(self, game_state):

        genome_id, genome = self.population_object.get_population()[self.genome_index]
        genome.fitness = game_state["distance_traveled"]

        num_segments = 11
        inputs = [0] * num_segments
        sensor_range = 350
        for i in range(num_segments):
            
            segment_top = -(sensor_range / 2.0) + (i * (float(sensor_range) / num_segments))
            segment_bottom = -(sensor_range / 2.0) + ((i + 1) * (float(sensor_range) / num_segments))
            segment_center = (segment_top + segment_bottom) / 2.0

            #print(segment_top)
            #print(segment_bottom)
            #print(game_state["player_dist_to_floor"])
            #print(game_state["player_dist_to_ceil"])
            #print()

            blocked = False
            if -game_state["player_dist_to_ceil"] > segment_top:
                blocked = True
            elif game_state["player_dist_to_floor"] < segment_bottom:
                blocked = True
            #elif segment_center < (game_state["player_y"] - game_state["next_gate_block_top"]) and segment_center > (game_state["player_y"] - game_state["next_gate_block_bottom"]):
                #blocked = True
            elif (game_state["player_y"] + segment_center) > game_state["next_gate_block_top"] and (game_state["player_y"] + segment_center) < game_state["next_gate_block_bottom"]:
                blocked = True

            if blocked:
                inputs[i] = 1
        
#        if inputs[1] == 1:
#            genome.fitness -= 2000

        self.genome_index += 1
        if self.genome_index == len(self.population_object.get_population()):
            self.population_object.finish_run()
            self.best = self.population_object.init_run(n=self.generations)
            print("###################################################################")
            print(self.best)
            print("###################################################################")
            self.genome_index = 0
        else:
            genome_id, genome = self.population_object.get_population()[self.genome_index]
            self.current_network = neat.nn.FeedForwardNetwork.create(genome, self.config)

    def get_action(self, game_state):
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

        inputs = list(game_state.values())[1:8]
        inputs[0] /= 500
        inputs[1] /= 50
        inputs[2] /= 500
        inputs[3] /= 500
        inputs[4] /= 500
        inputs[5] /= 500
        inputs[6] /= 500
        """

        num_segments = 11
        inputs = [0] * num_segments
        sensor_range = 350
        for i in range(num_segments):
            
            segment_top = -(sensor_range / 2.0) + (i * (float(sensor_range) / num_segments))
            segment_bottom = -(sensor_range / 2.0) + ((i + 1) * (float(sensor_range) / num_segments))
            segment_center = (segment_top + segment_bottom) / 2.0

            #print(segment_top)
            #print(segment_bottom)
            #print(game_state["player_dist_to_floor"])
            #print(game_state["player_dist_to_ceil"])
            #print()

            blocked = False
            #if -game_state["player_dist_to_ceil"] > segment_top:
            #    blocked = True
            #elif game_state["player_dist_to_floor"] < segment_bottom:
            #    blocked = True
            #elif segment_center < (game_state["player_y"] - game_state["next_gate_block_top"]) and segment_center > (game_state["player_y"] - game_state["next_gate_block_bottom"]):
                #blocked = True

            if (game_state["player_y"] + segment_center) > game_state["next_gate_block_top"] and (game_state["player_y"] + segment_center) < game_state["next_gate_block_bottom"]:
                blocked = True

            if blocked:
                inputs[i] = 1 / (game_state["next_gate_dist_to_player"] / 700)

        inputs.append(0.1 / (game_state["player_dist_to_ceil"] / 400))
        inputs.append(0.1 / (game_state["player_dist_to_floor"] / 400))
        inputs.append(game_state["player_vel"] / 50)

        #print(inputs)

        action = None
        output = self.current_network.activate(inputs)

        if output[0] >= output[1]:
            action = "up"

        return action
