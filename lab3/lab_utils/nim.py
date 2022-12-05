from collections.abc import Iterable
from typing import Union, Iterable
class Nim:
    def __init__(
        self, 
        data:Union[Iterable, int],
        player:str=None, 
        agent:str=None, 
        **kwargs) -> None:
        """
        Initialise Nim instance.

        Args:
            data (list or int, optional): if list, each element of a list represent the number of objects in a particular position. 
                                          if int, the game is a list of the odd numbers up to `data`. 
            player (str, optional): to keep track of the current player during a game. If specified, should be either 'human' or 'computer'. Defaults to None.
            agent (str, optional): if specified, the agent that finds the best move at each step. 
                                    Only accepts 4 values: omni, minimax, rl, rules, or None. (not case-sensitive). 

        Kwargs, defined when `agent` = rules:
            k (int): number of heaps that you want to eliminate during the opening. Default: number of heaps - 1.
            alpha (float, optional): probability of wiping the most populated heap. Its complementary is the probability of removing the least populated heap. Default to 0.9.
            endgame_nim (float, optional): percentage of elements to nim in endgame. Should be between 0 and 1. Default to 0.6.
            strategy (float, optional): strategy to adopt when nimming based on pairwise variances. 
                                        Each strategy is associated to a parameter beta meant to multiply each variance. 
                                        Given a strategy, bring to 0 the variance associated to the highest product (beta * pairwise_variance).
                                        Possible options:
                                        - None: beta = 1. Simply bring to 0 the highest pairwise variance
                                        - 'sum' : beta = sum of the two heap sizes. 
                                        - 'min' : beta = min(heap sizes pair)
                                        - 'max' : beta = max(heap sizes pair)
                                        Default: None
        Raises:
            ValueError: Data should be either of type list, or an integer.
        """
        if data is None: 
            raise ValueError("'data' cannot be empty. Please provide either an integer or a list (representing an actual configuration")
        
        if player is not None and player.lower() not in ["human", "computer"]: 
            raise ValueError("'player' must be either None or a string in [human, computer]. None corresponds to human player.")

        if isinstance(data, Iterable):
            # read configuration from input data, Iterable
            self._rows = list(data).copy()
        
        elif isinstance(data, int):
            self._rows = [i*2 + 1 for i in range(data)]
        else:
            raise ValueError('Data must be either an integer or an Iterable (try with tuple/list)')
        
        self.player = player
        self.agent = agent

        # default parameters are obtained using an extensive grid search
        self._k = kwargs.get("k", 1)
        self.alpha = kwargs.get("alpha", 0.)
        self.endgame_nim = kwargs.get("endgame_nim", 0.6)
        self.strategy = kwargs.get("strategy", None)

    def nimming(self, row:int=None, num_objects:int=None, target:list=None, switch_player=False) ->None:
        """
            Given a Nim instance, return the nimmed version.
        
        Args:
            row (int, optional): row you wish to nim. Defaults to None.
            num_objects (int, optional): number of objects you wish to nim. Defaults to None.
            target (list, optional): if `row` and `num_objects` are not specified, this is the target status AFTER nimming. Defaults to None.
            switch_player (bool) : if True, switch from self.player from 'human' to 'computer' and viceversa. Default to False.
        """
        if (row is not None and num_objects is not None) ^ (target is not None): 
            pass
        else:
            raise ValueError("Row and number of objects can be None. Target can be None. But they cannot be None at the same time!")
            
        if row is not None:
            # updating heap correspondent to index row
            if self._rows[row] < num_objects: 
                raise ValueError("Cannot remove from a row more elements that the ones in the row itself!")
            self._rows[row] -= num_objects
        else:
            # here the modification is done updating rows with input target 
            pairwise_diff = sorted([nim_before - nim_after for nim_before, nim_after in zip(self._rows, target)], reverse=True)
            if pairwise_diff[0] > 0 and pairwise_diff[1] != 0: 
                raise ValueError("Cannot remove elements from different rows!")
            self._rows = target

        if switch_player:
            assert self.player is not None # self player cannot be None
            self.player = 'human' if self.player == 'computer' else 'computer'

    def possible_new_states(self):
        """ 
            Given a Nim instance, return the next (legal) possible states.
            Only unique states are returned, i.e., if two lists contain the same numbers but in different positions,
            only one is returned.
        """
        horizon = [
            self._rows[:idx]+[n]+self._rows[idx+1:] if n_objects > 0 else 0 # putting element at index 'idx' equal to n
                for idx, n_objects in enumerate(self._rows) # looping over the rows
                    for n in range(n_objects) # looping over all possible 'n' in n_objects range.
                ]
        horizon_no_dupl = list(map(Nim, list({tuple(sorted(i)): i for i in horizon}.values())))
        return (horizon_no_dupl)

    def is_endgame(self):
        """
            Given a Nim instance game, check whether we are in endgame.
            Endgame happens when there is at most one heap with more than one object.
        """
        return (len([n_objects for n_objects in self._rows if n_objects > 1]) in [0, 1])

    def number_of_heaps(self):
        """
            Return the number of heaps in a Nim instance
        """
        return (len(self._rows))

    def nim_sum(self):
        """
            Given a Nim game, return the corresponding nim-sum, i.e. XOR sum
        """
        nim_sum = self._rows[0]
        for i in range(1, self.number_of_heaps()):
            nim_sum = nim_sum ^ self._rows[i]
        return nim_sum

    def biggest_heap(self):
        """
            Given a game, return the heap with the maximum number of objects.
        """
        return max(enumerate(self._rows), key=lambda x: x[1])[0]

    def smallest_heap(self):
        """
            Given a game, return the heap with the smallest number of objects.
        """
        return min(enumerate(self._rows), key=lambda x: x[1])[0]

    def print_nim(self):
        """
            Graphic function to visualise the game.
        """
        for i in range(len(self._rows)):        
            print(f"[{i}][{self._rows[i]} elements] ", end = " ")
            for j in range(self._rows[i]):            
                print("* ",end="")        
            print("\r")