from __future__ import print_function
import os
import neat
from .population import *

# Initial skeleton for agents
class Agent():

    def __init__(self, generations=300):

        local_dir = os.path.dirname(__file__)
        config_file = os.path.join(local_dir, 'config-feedforward')

        self.iterations = 0
        self.generations = generations

        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

        #self.population_object = neat.Population(config)
        self.population_object = Population(self.config)

        self.population_object.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.population_object.add_reporter(self.stats)
        self.population_object.add_reporter(neat.Checkpointer(5))

        self.population, self.config = self.population_object.init_run(n=self.generations)
        self.genome_index = 0
        self.genome_id, self.current_genome = self.population[self.genome_index]
     
        self.current_genome.fitness = 0
        self.current_network = neat.nn.FeedForwardNetwork.create(self.current_genome, self.config)

    # This is the name of the constructor used by the game.
    # Be sure to call the actual constructor here.
    def Agent(self):

        self.__init__()

    def reset(self, game_state):

        #print(self.population)
        self.current_genome.fitness = game_state["distance_traveled"]
        #self.population[self.genome_index][1].fitness = game_state["distance_traveled"]

        #print("distance_traveled: %s, current_genome.fitness: %s" %(game_state["distance_traveled"], self.current_genome.fitness))
        #print("this type: %s" % (type(game_state["distance_traveled"])))

        if self.genome_index == len(self.population) - 1:
            print(self.population_object.generation)
            print("lololololol")
            self.population_object.finish_run()
            self.genome_index = 0
        
        self.genome_index += 1
        self.genome_id, self.current_genome = self.population[self.genome_index]
        #self.current_genome = self.population[self.genome_index][1]
        self.current_genome.fitness = 0
        self.population[self.genome_index][1].fitness = 0
        self.current_network = neat.nn.FeedForwardNetwork.create(self.current_genome, self.config)
 
#        if self.iterations < self.generations:
#            self.iterations += 1
#            #self.population, self.config = self.population_object.init_run(self.generations)
#            self.genome_index = 0
#            self.genome_id, self.current_genome = self.population[self.genome_index]
#            #self.current_genome = self.population[self.genome_index][1]
#            self.current_genome.fitness = 0
#            self.population[self.genome_index][1].fitness = 4
#            self.current_network = neat.nn.FeedForwardNetwork.create(self.current_genome, self.config)

    def get_action(self, game_state):

        game_state = list(game_state.values())

        action = None

        output = self.current_network.activate(game_state)[0]

        if output > 0:
            action = "up"

        return action
