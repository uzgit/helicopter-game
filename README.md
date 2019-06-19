# Helicopter Game

This is a helicopter game adapted from PyGame Learning Environment's Pixelcopter, available at https://github.com/ntasfi/PyGame-Learning-Environment

This project is for Intelligent Systems at Mälardalens Högskola. It involves several learning algorithms that learn how to play the game.

## [See NEAT playing the helicopter game here](https://youtu.be/JuPe_nolOt0)

![Screenshot of helicopter game](https://github.com/uzgit/helicopter-game/blob/master/images/screenshot_with_helicopter.png)

Clipart for the helicopter is taken from https://www.clipartmax.com/download/m2i8K9i8b1A0b1N4_free-to-use-public-domain-transportation-clip-art-helicopter-clipart/

---

## Prerequisites:

* ```argparse```
* ```matplotlib```
* ```numpy```
* ```pygame```
* ```graphviz```

## Included Libraries:

* ```pygamewrapper```
* ```vec2d```

## Usage:

For a human player:

```./pixelcopter.py```


To control the simulation speed (frames per second):

```./pixelcopter.py --fps 999```

The default value is 30 fps.


For an AI agent player whose class is stored in the agents/ subdirectory and called ```stupid_agent.py```:

```./pixelcopter.py --agent stupid_agent```


To run the game using noisy positioning data:

```./pixelcopter.py --agent stupid_agent --noisy-sensors```


To run the game without animation (```--quiet-mode```), for quicker testing of an agent:

```./pixelcopter.py --fps 4000 --agent stupid_agent --quiet-mode --headless```


By default, the game is in 'flappy' mode, like in Flappy Bird. However, it can be run in 'helicopter' mode:

```./pixelcopter.py --mode helicopter```


## Agent Structure

Agents must be contained in a uniquely-named ```.py``` file within a class ```Agent```. Agent selection and import is done at the terminal at runtime as described above. Agents must contain the following functions:

* ```Agent(self)``` is the constructor called by the game.
* ```get_action(self, game_state)``` is called by the game once per frame. It supplies the agent with the current state of the game and expects an action.
* ```reset(self, game_state)``` is called by the game in the event of a game-over.

## Agent Inputs

* ```normalized_heights```: array of normalized values representing the helicopter's closeness to the top and bottom of each of the next 3 terrain sections.
* ```sensors```: 5 proximity sensors aimed in front of the helicopter. 0 means no obstacle. Anything above 0 represents an obstacle at the height of the sensor, and increases to 1 as the obstacle becomes closer.
* ```y_velocity```: how quickly the helicopter is moving upwards or downwards. Not normalized.
