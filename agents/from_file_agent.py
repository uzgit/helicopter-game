# This agent is used to examine the behavior of a genome that has already been
# generated and saved to a file.

from .neat.genome import *
from .neat.neural_network import *

genome_file = "/home/joshua/PycharmProjects/helicopter-game/agents/champion.genome"

class Agent():

    def __init__(self):

        self.genome = Genome.from_file(genome_file)
        self.neural_network = FeedForwardNeuralNetwork(self.genome)

        self.outputs = {0: None, 1: "up"}

    def reset(self, game_state):

        print("Reset requested by game. Distance traveled this run: %0.2f" % (game_state["distance_traveled"]))

    def get_action(self, game_state):

        inputs = [height_ratio for height_ratio in game_state["height_ratios"]]
        inputs += [segment for segment in game_state["segments"]]
        inputs.append(game_state["player_vel"] / 50)

        action = self.outputs.get( self.neural_network.activate(inputs)[0], None )

        return action
