import sys
from datetime import datetime

from .neat.functions import *
from .neat.population import *
from .neat.neural_network import *
from .neat.visualize import *

class Agent():

    def __init__(self):

        self.num_inputs = 12
        self.num_outputs = 1
        self.initial_num_hidden_nodes = 0
        self.max_num_hidden_nodes = 10
        self.output_activation_function = step

        self.num_generations = None
        self.fitness_goal = 100000

        self.output_stream_name = "sys.stdout"

        self.outputs = {0 : None, 1 : "up"}

        self.champion = None
        self.generation_champion = None

        self.population = Population(num_inputs=self.num_inputs, num_outputs=self.num_outputs, initial_num_hidden_nodes=self.initial_num_hidden_nodes, max_num_hidden_nodes=self.max_num_hidden_nodes, output_activation_function=step, output_stream_name=self.output_stream_name)
        self.population.pre_evaluation_tasks()

        self.neural_network_iterator = iter(self.population.neural_networks)
        self.neural_network = next( self.neural_network_iterator, None )

    def get_action(self, game_state):

        # height ratios has 4 elements
        # inputs = [height_ratio for height_ratio in game_state["height_ratios"]]

        # normalized heights has 6 elements
        inputs = [normalized_height for normalized_height in game_state["normalized_heights"]]

        # segments has 5 elements by default
        inputs += [segment for segment in game_state["segments"]]

        inputs.append(game_state["player_vel"] / 50)

        action = self.outputs.get( self.neural_network.activate(inputs)[0], None )

        return action

    def reset(self, game_state):

        print(end="\r")
        print(" "*100, end="\r")
        print("Reset requested by game. Network {} traveled a distance of {}.".format(self.neural_network.identifier, round(game_state["distance_traveled"], 2)), end="\r")

        # Set the fitness of the genome of the current neural network and go to the next neural network.
        self.neural_network.genome.fitness = game_state["distance_traveled"]
        self.neural_network = next( self.neural_network_iterator, None )

        # If we have evaluated all neural networks in the generation:
        if self.neural_network is None:
            print(end="\r")
            print(" "*100, end="\r")
            self.champion, self.generation_champion = self.population.post_evaluation_tasks()

            # draw_neural_network_full(FeedForwardNeuralNetwork(self.champion), "champion")
            # draw_neural_network_full(FeedForwardNeuralNetwork(self.generation_champion), "generation_champion")

            self.population.pre_evaluation_tasks()

            if not self.population.continue_run(num_generations=self.num_generations, fitness_goal=self.fitness_goal):
                self.population.save("neat_agent_gen{}_{}.population".format(self.population.generation, str(datetime.now()).replace(" ", "-")))
                return "quit"

            else:
                self.neural_network_iterator = iter(self.population.neural_networks)
                self.neural_network = next(self.neural_network_iterator, None)
