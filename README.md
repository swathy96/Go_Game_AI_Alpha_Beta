# Alpha_Beta_Player_For_Go_game
A small agent that plays against a random move player in the game of go of the board size 5 X 5.

# host.py
Host is where the game is initialized and the players play the game.
The black player is X and the white is O.
The game is played 15 times to check if the AI Agent plays perfectly.

# random_player.py
A agent that takes random valid move. It cares nothing about winning.

# my_player3.py
An alpha beta agent of depth 2 choosing best moves based on the move made by the random player, and the max score it might get based on the move.
