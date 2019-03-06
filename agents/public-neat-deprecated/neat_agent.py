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

        self.genome_index += 1
        if self.genome_index == len(self.population_object.get_population()):
            self.population_object.finish_run()
            self.population_object.init_run(n=self.generations)
            self.genome_index = 0
        else:
            genome_id, genome = self.population_object.get_population()[self.genome_index]
            self.current_network = neat.nn.FeedForwardNetwork.create(genome, self.config)

    def get_action(self, game_state):
        
        inputs = list(game_state.values())[1:]

        action = None
        output = self.current_network.activate(inputs)

        if output[0] >= output[1]:
            action = "up"

        return action
