# Stupid agent just presses up every 11 steps, then quits after 200 steps
class Agent():

    def __init__(self):

        self.iterations = 0
        self.activation_threshold = 10

    def reset(self):

        self.__init__()

    def get_action(self, game_state):

        action = None

        self.iterations += 1

        if(game_state["player_dist_to_ceil"] > game_state["player_dist_to_floor"]):
            self.activation_threshold = 10
        else:
            self.activation_threshold = 11

        if(self.iterations % self.activation_threshold == 0):

            action = "up"

        if(self.iterations == 400):

            action = "quit"
        
#        if action == "up":
#            print("%s up" % self.iterations)
#        else:
#            print("%s None" % self.iterations)

        return action
