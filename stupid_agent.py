# Stupid agent just presses up every 11 steps, then quits after 200 steps
class Agent():

    def __init__(self):

        self.iterations = 0

    def reset(self):

        self.__init__()

    def get_action(self, game_state):

        action = None

        self.iterations += 1
        if(self.iterations % 11 == 0):

            action = "up"

        if(self.iterations == 200):

            action = "quit"

        return action
