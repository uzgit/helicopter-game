import sys

from .neat.functions import *
from .neat.population import *

class Agent():

    def __init__(self):

        self.num_inputs = 8
        self.num_outputs = 1
        self.initial_num_hidden_nodes = 0
        self.max_num_hidden_nodes = 10
        self.output_activation_function = step

        self.num_generations = None
        self.fitness_goal = 50000

        self.output_stream = sys.stdout

        self.outputs = {0 : None, 1 : "up"}

        self.population = Population(num_inputs=self.num_inputs, num_outputs=self.num_outputs, initial_num_hidden_nodes=self.initial_num_hidden_nodes, max_num_hidden_nodes=self.max_num_hidden_nodes, output_activation_function=step, output_stream=self.output_stream)
        self.population.pre_evaluation_tasks()

        self.neural_network_iterator = iter(self.population.neural_networks)
        self.neural_network = next( self.neural_network_iterator, None )

    def get_action(self, game_state):

        inputs = [height_ratio for height_ratio in game_state["height_ratios"]]
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
            self.population.post_evaluation_tasks()
            self.population.pre_evaluation_tasks()

            if not self.population.continue_run(num_generations=self.num_generations, fitness_goal=self.fitness_goal):
                return "quit"

            else:
                self.neural_network_iterator = iter(self.population.neural_networks)
                self.neural_network = next(self.neural_network_iterator, None)
