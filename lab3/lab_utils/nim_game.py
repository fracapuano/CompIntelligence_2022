from lab_utils.nim_omni import *
from lab_utils.nim_rules import *

def play(nim_game:object, inplace_move:bool=True)->None:
        """This funtion plays the actual game. Human vs computer. Human starts first.

        Args:
            nim_game (object, Nim): instance of a pre-generated Nim game
            inplace_move (bool): Whether to perform the move on Nim game or not. Defaults to True.
        """

        # Keep a copy of the original game if the player wants to play again at the end of a match
        original_game = Nim(nim_game._rows.copy())

        while True:                
            if nim_game.player is None:
                nim_game.player = 'human'
            
            if nim_game.agent is None:
                nim_game.agent = 'omni'

            while sum(nim_game._rows) > 0:
                print("Current situation: ")
                nim_game.print_nim()
                user_input = input('Please, insert the row you want to nim and how many objects, divided by a blank space, e.g. -> 0 1\n')
                row_to_nim, objects_to_nim = tuple(int(x) for x in user_input.split(' '))

                nim_game.nimming(row = row_to_nim, num_objects = objects_to_nim, switch_player = True)
                nim_game.print_nim()

                if sum(nim_game._rows) == 0:
                    print("I.. I... don't know what to say. You've won! gg")
                    break

                print('Hmm... nice move. Very brave of you! My go now!')
                # omiscent agent, one playing *knowing* how to win
                if nim_game.agent == 'omni':
                    if inplace_move: 
                        best_move_nim_sum(nim_game, inplace=inplace_move)
                    else: 
                        print("Best move: ", best_move_nim_sum(nim_game, inplace=inplace_move))
                # agent playing according to parametric rules
                elif nim_game.agent == 'rules':
                    if inplace_move: 
                        best_move_rules(nim_game, inplace=inplace_move)
                    else: 
                        print("Best move: ", best_move_rules(nim_game, inplace=inplace_move))

                if sum(nim_game._rows) > 0:
                    print("Ha-ha! I've got you! Go on you fool ;)")
                
                else: 
                    nim_game.print_nim()
                    print("LOSER looool eheheh L2P N00B MAYBE NEXT TIME ♥")
                    break               

            repeat_game = input("Do you want to play again? ['Enter' to play again/any other key to exit] ")
            if repeat_game == "": # repeat the game
                agent = input("Against what agent? [omni/rules] ")
                nim_game = Nim(original_game._rows.copy())
                nim_game.agent = agent    
            else: 
                print("Game over")
                break