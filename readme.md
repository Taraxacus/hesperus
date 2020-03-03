

### Remarks for coders

#### Coding Conventions
  * Use underscores, not camel case!

  * Coordinates of vectors are given by tuples of length two.
The vector (1,0) points straight upwards.
The vector (0,1) points right and downwards, 120 degrees to the first vector.
Both basis vectors have length specified by the HEX_LENGTH variable below.
  * Abbreviations:

    L - lumber,

    B - brick,

    G - grain,

    W - wool,

    O - ore,

    D - desert.

#### Files

  * gamestate.py: Defines the GameState class which saves information about the
    state of the game.
  * player.py: Introduces some minimal AIs necessary to run test games
  * game.py: Defines the run function which plays runs a game
  * ui.py: Defines two user interfaces. One is based solely on the
    command-line, the other uses turtle graphics to display the game.
  * simulation.py: Supplies tools for running simulations of the game without player
  * main.py: **Execute this file to enjoy the game!**

#### Dependency diagram

![alt-text](/images/graph.png)
