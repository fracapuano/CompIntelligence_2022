from typing import Union
def best_move_nim_sum(nim_game:object, inplace:bool=False)->Union[None, list]:
    """
        Given a Nim game, return the best move based on nim-sum.
        To an explanation of nim-sum, please refer to: https://en.wikipedia.org/wiki/Nim#Mathematical_theory
    
    Args:
        nim_game (object, Nim): Nim instance where to evaluate the best move.
        inplace (bool): whether the function should return the best move as a list or if it should operate it right away.
    
    Returns:
        Union[None, list]: Either None (best move is performed on nim_game) or the list representing the best move.
    """
    if not nim_game.is_endgame():
        # computing nim_sum as per documentation
        nim_sum = nim_game.nim_sum()

        if nim_sum == 0:
            # opponent made their possible best move.
            # remove one object from the most populated row (minimising other's time-to-win).
            if inplace:
                # perform the best move on the actual game
                nim_game.nimming(nim_game.biggest_heap(), 1, switch_player = True)   
            else:
                # return the best move (decreasing by one most populated heap)
                rows_copy = nim_game._rows.copy()
                # decreasing most populated heap
                rows_copy[nim_game.biggest_heap()] -= 1

                return (rows_copy)
        else:
            # opponent does not play their best move
            # bring the game to nim-sum 0 removing the maximum number of elements
            nim_differences = [heap - (heap ^ nim_sum) for heap in nim_game._rows]
            # obtaining the index of largest difference in nim_differences

            biggest_difference = max(enumerate(nim_differences), key=lambda x: x[1])[0]

            if inplace:
                # perform the best move on the actual game
                nim_game.nimming(biggest_difference, nim_differences[biggest_difference], switch_player = True)
            else:
                # return the best move (decreasing by biggest_difference populated heap)
                rows_copy = nim_game._rows.copy()
                # decreasing most populated heap
                rows_copy[biggest_difference] -= nim_differences[biggest_difference]

                return (rows_copy)
           
    else: # match is in endgame
        row, objects_to_nim = endgame_nim_sum(nim_game)
        if inplace:
            nim_game.nimming(row, objects_to_nim, switch_player = True)
        else:
            rows_copy = nim_game._rows.copy()
            # decreasing heap at index row by objects_to_nim amount
            rows_copy[row] -= objects_to_nim
            
            return (rows_copy)

def endgame_nim_sum(nim_game):
    """
        Given a Nim game, find the best move to reach the goal when in endgame.  

    Args:
        nim_game (Nim)
    Returns:
        list: 2-element list. First element is the row where to operate the nim, second element is how many objects you want to nim.
    """
    # I need to leave an even number of objects
    biggest_heap_pos = nim_game.biggest_heap()
    objects_left = sum(nim_game._rows[:biggest_heap_pos] + nim_game._rows[1 + biggest_heap_pos:])
    if objects_left % 2 == 0 or max(nim_game._rows) == 1:
        return([biggest_heap_pos, max(nim_game._rows)])
    else:
        return([biggest_heap_pos, max(nim_game._rows) - 1])
