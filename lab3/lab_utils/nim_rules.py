from lab_utils.nim import *
import random
import itertools
from tqdm import tqdm
import pandas as pd
from typing import Union
from math import ceil
import numpy as np

def best_move_rules(nim_game:object, inplace:bool=False)->Union[None, list]:
    """This function either performs or return a best move based on a set of parametric rules.

    Args:
        nim_game (object): Nim game as per nim interface.
        inplace (bool, optional): Whether to perform the move on the actual nim_game or return it. Defaults to False.

    Returns:
        Union[None, list]: Either None (best move is performed on nim_game) or the list representing the best move.
    """
    # opening:
    opening_condition = nim_game._rows.count(0) + nim_game._rows.count(1) < nim_game._k
    
    if not nim_game.is_endgame() and opening_condition:
        opening_move = opening(nim_game, nim_game.alpha)
        
        if inplace:
            nim_game.nimming(target = opening_move)
        else:
            return (opening_move)

    # midgame:    
    elif not nim_game.is_endgame():
        midgame_move = midgame(nim_game, nim_game.strategy)
        
        if inplace:
            nim_game.nimming(target = midgame_move)
        else:
            return (midgame_move)
    
    # endgame:
    elif sum(nim_game._rows) > 0:
        biggest_heap = nim_game.biggest_heap()
        # not possible to nim zero elements
        elements_to_nim = max(
            ceil(nim_game.endgame_nim * nim_game._rows[biggest_heap]), 1
        )
        if inplace:
            nim_game.nimming(biggest_heap, elements_to_nim)
        
        else:
            target = nim_game._rows.copy()
            target[biggest_heap] -= elements_to_nim

            return (target)

def opening(nim_game:object, alpha:float)->list:
    """This function is used in the opening phase.
    With probability alpha nims biggest heap and 1-alpha nims smallest heap. 

    Args:
        nim_game (object): Nim game as per nim interface.
        alpha (float): Probability of nimming biggest heap during opening. 1-alpha is the probability of nimming smallest
                       heap during opening.

    Returns: 
        list: list representing the configuration corresponding to best move according to parameter.
    """
    if random.uniform(0, 1) < alpha:
        biggest_heap = nim_game.biggest_heap()
        # target configuration
        target = nim_game._rows.copy()
        target[biggest_heap] = 0

        return (target)
    else:
        smallest_heap = nim_game.smallest_heap()
        # target configuration
        target = nim_game._rows.copy()
        target[smallest_heap] = 0

        return (target)

def midgame(nim_game:object, strategy:Union[str, None])->list:
    """This function is used in the midgame phase.
    It computes all the pairwise variances between number of elements in the heaps and then performs one of the actions which
    decreases to 0 the maximal variance. The pairwise variance is weighted according to different strategies.

    Args:
        nim_game (object, Nim):  Nim game as per nim interface.
        strategy (Union[str, None]): Either 'None' when pairwise variances are not weighted according to any strategy or
                                     one in "min", "max" or "sum".
                                     "min" weighs each pairwise variance by the minimal value of the elements with respect to 
                                     is computed, "max" the maximal value and "sum" the sum of the values.

    Returns:
        list: target configuration to reduce maximal (according to strategy) pairwise variance.
    """
    # sanity check on strategy value
    if strategy is not None and strategy.lower() not in ["min", "max", "sum"]: 
        raise ValueError('Strategy must be one of ["min", "max", "sum"]. Check documentation for guidance in the choice') 

    # maximal variance between heaps
    variance_heaps = find_max_weighted_variance(nim_game, strategy)
    low, high = variance_heaps
    # variance_heaps = (
    #                   (low_idx, low_val), 
    #                   (high_idx, high_val)
    #                  )
    low_idx, low_val = low
    high_idx, high_val = high

    # rows copy
    rows_copy = nim_game._rows.copy()
    # making sure that the variance is either 0 or is minimized (when low_val = 0)
    rows_copy[high_idx] = min(max(1, low_val), high_val - 1)

    return (rows_copy)

def find_max_weighted_variance(nim_game:object, strategy:Union[str, None])->tuple:
    """Given a nim_game and a strategy, return the variance-sorted tuple of tuples indicating
    indices and values that need to be nimmed to minimise variance. 

    Args:
        nim_game (object, Nim): Nim game as per nim interface.
        strategy (Union[str, None]): Either 'None' when pairwise variances are not weighted according to any strategy or
                                     one in "min", "max" or "sum".
                                     "min" weighs each pairwise variance by the minimal value of the elements with respect to 
                                     is computed, "max" the maximal value and "sum" the sum of the values.

    Returns:
        tuple: Tuple of tuples of type (index, value) sorted according to value in ascending order.
    """
    # restricting to populated heaps only (those having at least one element inside)
    populated_heaps = [heap for heap in nim_game._rows if heap > 0]
    # edge case 1 - one heap only is populated (not going to be called if endgame is defined as per definition)
    if len(populated_heaps) == 1:
        first_zero_index = next(idx for idx, heap in enumerate(nim_game._rows) if heap == 0) 
        nonzero_index = next(idx for idx, heap in enumerate(nim_game._rows) if heap > 0)

        return (
            (first_zero_index, nim_game._rows[first_zero_index]), 
            (nonzero_index, nim_game._rows[nonzero_index])
            )
    # edge case 2 - configuration is like [n, n, n, ..., n]
    elif all_equal(populated_heaps):
        first_index, second_index = [idx for idx, heap in enumerate(nim_game._rows) if heap > 0][:2]
        return (
            (first_index, nim_game._rows[first_index]), 
            (second_index, nim_game._rows[second_index])
            )
    # non-edge cases
    strategy_dict = {"min" : min, "sum" : sum, "max" : max}
    # different pairs
    combinations = list(itertools.combinations(populated_heaps, 2))
    if strategy is None:
        # beta is a weight array with length equal to the number of pairs obtainable from populated_heaps
        beta = [1] * len(combinations)
    else:
        # beta is a weight array with length equal to the number of pairs obtainable from populated_heaps
        # elements of beta are the results of applying strategy to the possible pairs
        beta = [strategy_dict[strategy](tuple_) for tuple_ in combinations]
    
    # computing variances
    pairwise_vars = [
        (tuple_[0] - (sum(tuple_) / 2)) ** 2 + (tuple_[1] - (sum(tuple_) / 2)) ** 2
            for tuple_ in combinations
            ]
    # weighting pairwise variances
    weighted_pairwise_vars = [beta[i] * var for i, var in enumerate(pairwise_vars)]
    
    # values corresponding to maximal variance 
    values_max_var = sorted(list(combinations)[max(enumerate(weighted_pairwise_vars), key=lambda x: x[1])[0]])
    # sorting values of maximal variance in ascending order gives the desidered ordering in output (low to high)
    
    return (
        (next(idx for idx, heap in enumerate(nim_game._rows) if heap == values_max_var[0]), values_max_var[0]),
        (next(idx for idx, heap in enumerate(nim_game._rows) if heap == values_max_var[1]), values_max_var[1])
        )

def rules_tournament(nim_game:object)->pd.DataFrame:
    """This function returns a pd.DataFrame with the result of the tournament for various parameters.

    Args:
        nim_game (object, Nim): Nim game as per nim interface.

    Returns:
        pd.DataFrame: DataFrame containing experiments results
    """
    gridsearch = {
        "k" : range(0, nim_game.number_of_heaps()),
        "alpha" : np.linspace(start = 0, stop = 1, num = 20, endpoint = False),
        "endgame_nim" : np.linspace(start = 0.05, stop = 1, num = 19, endpoint = False),
        "strategy" : ['sum', 'min', 'max', None]
    }
    
    keys, values = zip(*gridsearch.items())
    permutations_dicts = [dict(zip(keys, v)) for v in itertools.product(*values)]

    championship = pd.DataFrame(permutations_dicts)
    
    winning_ratio = []
    n_games = int(1e2)

    for dict_ in tqdm(permutations_dicts, desc = 'Configuration'):    
        # using dict as kwargs
        nim_gym = Nim(
            nim_game._rows.copy(), agent = 'rules', **dict_)
        # array in which each element corresponds to either 1 (win) or 0 (loss)
        palmares = rules_gym(nim_gym, n_games = n_games)
        winning_ratio.append(sum(palmares) / len(palmares))
    
    # storing information on percentage of games won
    championship["success"] = winning_ratio

    return (championship)

def rules_gym(test_agent:object, n_games:int=100):
    """Gym for the rule-based agent. The goal is to find the one which performs better than the random agent.

    Args:
        test_agent (object, Nim):  Nim game as per nim interface.
        n_games (int, optional): total number of games. Defaults to 100.
    """
    original_nim = test_agent._rows.copy()
    palmares = []

    for _ in range(n_games): 
        test_agent._rows = original_nim.copy()
        while sum(test_agent._rows) > 0: # as long as one can play, play
            # test agent performs best move according to rules
            best_move_rules(test_agent, inplace = True)                
            
            if sum(test_agent._rows) == 0:
                palmares.append(1)
                break
            
            row = random.choice([r for r, c in enumerate(test_agent._rows) if c > 0])
            num_objects = random.randint(1, test_agent._rows[row])
            # control agent performs random move
            test_agent.nimming(row, num_objects)

            if sum(test_agent._rows) == 0: # once control agent wins, stop playing and register loss
                palmares.append(0)
                break

    return (palmares)

def all_equal(l:Iterable)->bool:
    """This function returns a boolean value indicating whether or not a given list contains all equal values.

    Args:
        l (Iterable): Iterable

    Returns:
        bool: Whether or not l contains only identical values
    """
    g = itertools.groupby(l)
    return next(g, True) and not next(g, False)