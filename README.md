# Helicopter Game

This is a helicopter game adapted from PyGame Learning Environment's Pixelcopter, available at https://github.com/ntasfi/PyGame-Learning-Environment

This project is for Intelligent Systems at Mälardalens Högskola. It involves several learning algorithms that learn how to play the game.

![Screenshot of helicopter game](https://github.com/uzgit/helicopter-game/blob/master/images/screenshot_with_helicopter.png)

Clipart taken from https://www.clipartmax.com/download/m2i8K9i8b1A0b1N4_free-to-use-public-domain-transportation-clip-art-helicopter-clipart/

## Prerequisites:

* ```argparse```
* ```numpy```
* ```pygame```

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

To run the game without animation (```--quiet-mode```), for quicker testing of an agent:
```./pixelcopter.py --fps 4000 --agent stupid_agent --quiet-mode```
