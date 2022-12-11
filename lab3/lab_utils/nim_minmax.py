from lab_utils.nim import Nim
from functools import cache

@cache
def minmax(nim_game, maximising = True):
    """
        Recursive function which, given a Nim game and the goal of the current player (min / max), returns the minmax value.
        The method is already alpha-beta pruned.

    Args:
        nim_game (Nim)
        maximising (bool, optional): whether the goal is to maximise. If False, the goal is to minimise. Defaults to True.

    Returns:
        integer: minmax value
    """
    # Check if the game is finished
    if sum(nim_game._rows) == 0:
        return -1 if maximising else 1

    # if not, analyse all possible new states and the corresponding scores
    # this is done with a recursive function, where each time the value
    # of `maximising` is negated -> max, min, max, min, ...
    scores = []
    for new_state in nim_game.possible_new_states():
        score = minmax(new_state, maximising = not maximising)
        scores.append(score)
        # ALPHA-BETA PRUNING:
        # we noticed that it works perfectly, but when the number of rows is big (>15), the tree is still too big
        # and the computation is extremely slow
        if maximising:
            alpha = max(-1, score)
            beta = 1
        else:
            alpha = -1
            beta = min(1, score)
        if beta <= alpha:
            break
    return (max if maximising else min)(scores)

def best_move_minmax(nim_game, inplace = False):
    """
        Given a Nim game instance, work out the best minmax move.

    Args:
        nim_game (Nim)
        inplace (bool, optional): if True, the best minmax is already applied and `nim_game` is nimmed accordingly

    Returns:
        Nim: the best move is returned as a Nim object if `inplace` is True, otherwise `nim_game` is pruned according to the best move.
    """
    maximising = True
    for i, new_state in enumerate(possible_states := nim_game.possible_new_states()):
        # compute the score of the next move (assuming to in the opponent's shoes)
        score = minmax(new_state, maximising = not maximising)
        # the product makes sure the 'best' move is always positive, regardless of the player
        if score * (1 if maximising else -1) > 0:
            if inplace:
                nim_game.nimming(target = new_state._rows)
                break
            else:
                return new_state._rows
        elif i == len(possible_states) - 1:
            # our opponent made their possible best move.
            # remove one object from the most populated heap.
            nim_game.nimming(nim_game.biggest_heap(), 1)
            
