# Stupid agent just presses up every 11 steps, then quits after 200 steps
class Agent():

    def __init__(self):

        self.iterations = 0
        self.activation_threshold = 10
        self.target_distance = 4000

    def reset(self, game_state):

        print("Reset requested by game. Distance traveled this run: %0.2f" %(game_state["distance_traveled"]))
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

        if(game_state["distance_traveled"] >= self.target_distance):
            
            print("Stupid agent reached a distance of %0.2f with target distance of %0.2f" %(game_state["distance_traveled"], self.target_distance))
            action = "quit"
        
#        if action == "up":
#            print("%s up" % self.iterations)
#        else:
#            print("%s None" % self.iterations)

        return action
