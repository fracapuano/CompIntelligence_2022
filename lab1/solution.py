from itertools import product
from lab_utils import Problem, TupleSet
from gx_utils import PriorityQueue

import logging
import random
from typing import Callable, Tuple

# flatten out a tuple of tuples
def flatten(d): 
        for i in d:
            yield from [i] if not isinstance(i, tuple) else flatten(i)

class SolvedProblem: 
    def __init__(self, N:int, seed:int = None): 
        self.problem = Problem(N = N, seed = seed)
    
    def heuristic(self, state:TupleSet):
        flattened_state = flatten(state.tuples)
        return len((self.problem.goal).difference(set(state.count.keys())))

    def set_functions(self)->list:
        """This function sets the different priority functions used to define the frontier.

        Returns:
            list: List of priority functions defined for current problem.
        """
        self.BF = lambda s: len(self.state_cost)
        self.custom_heuristic = lambda s: self.heuristic(s)
        return [self.BF, self.custom_heuristic]
    
    def search(
        self, 
        initial_state: tuple = None,
        priority_function: Callable = None
    )->TupleSet: 
        """This function perform search. 

        Args:
            initial_state (tuple): Initial state from which to start searching.
            priority_function (Callable): Priority function to be used in exploration of queue.

        Returns:
            TupleSet: Object storing the full optimization trajectory.
        """
        self.frontier = PriorityQueue()
        self.state_cost = {}
        if initial_state is None: 
            random.seed(self.problem.seed)
            initial_state = random.choice(max(self.problem.P, key = len))
        if priority_function is None: 
            priority_function = lambda arg: len(self.state_cost)
        
        # initializations
        state = TupleSet(tup = initial_state)
        self.state_cost[state.tuples] = 0

        while state is not None and not self.problem.test_candidate(state):
            for a in self.problem.possible_actions(state):
                new_state = state.result(a)
                cost = self.problem.compute_cost(TupleSet(new_state))
                if new_state not in self.state_cost and new_state not in self.frontier:
                    self.state_cost[new_state] = self.state_cost[state.tuples] + cost
                    self.frontier.push(new_state, p=priority_function(TupleSet(new_state)))
                    logging.debug(f"Added new node to frontier (cost = {self.state_cost[new_state]})")
                if new_state in self.frontier and self.state_cost[new_state] > self.state_cost[state.tuples] + cost:
                    old_cost = self.state_cost[new_state]
                    self.state_cost[new_state] = self.state_cost[state] + cost
                    logging.debug(f"Update node cost in frontier: {old_cost} -> {self.state_cost[new_state]}")
            if self.frontier:
                performed_action = self.frontier.pop()[-1]
                state.register_new(new_tup = performed_action)
            else:
                state = None
        return state

def main(): 
    problem_size = [5, 10, 20, 50, 100, 500]
    functions = ["Breadth First"] # to be further modified adding new functions

    for function, size in product(functions, problem_size): 
        sp = SolvedProblem(N = size, seed = 42)

        if not sp.problem.is_solvable(): 
            raise Exception("Problem is not solvable!")
        
        result = sp.search(priority_function=None) # to be further modified
        
        print(f"With priority function {function} and size {size}:\n")
        print(f"\tSolution's cost: {sp.state_cost[result.tuples]}\n\ visiting a total of {len(sp.state_cost):,} nodes")

        # to be used as a sanity check
        # print(result.count)

if __name__ == "__main__": 
    main()