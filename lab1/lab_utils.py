from collections import Counter
import random
from typing import Generator, Iterable

def problem(N: int, seed:int=None)->Generator:
    """Returns a generator for given value of N. 

    Args:
        N (int): Value of N to be used for the problem considered.
        seed (int, optional): Random seed to be used for random initialization_. Defaults to None.

    Returns:
        Generator: Generator object defined with a list comprehension according to problem specification.
    """
    random.seed(seed)
    return [
        list(set(random.randint(0, N - 1) for n in range(random.randint(N // 5, N // 2))))
        for n in range(random.randint(N, N * 5))
    ]

class TupleSet: 
    def __init__(self, tup:tuple): 
        # sorting input tuple
        tup = tuple(sorted(tup))
        # store seen tuples
        self.tuples = tup
        # store counter of visualized numbers
        self.count = Counter()
        if tup:
            for item in tup: 
                self.add(item)
    
    def __hash__(self) -> int:
        return hash(bytes(self.count))
    
    def __eq__(self, other: "TupleSet"):
        return bytes(self) == bytes(other)

    def __le__(self, other: "TupleSet"):
        for i, n in self.count.items():
            if other.count(i) < n:
                return False
        return True
    
    def __lt__(self, other: "TupleSet"):
        return self <= other and not self == other

    def __ge__(self, other: "TupleSet"):
        return other <= self

    def __gt__(self, other: "TupleSet"):
        return other < self
    
    def add(self, item, *, cnt=1):
        assert cnt >= 0, "Can't add a negative number of elements"
        if cnt > 0:
            self.count[item] += cnt
    
    def register_new(self, new_tup:tuple)->None: 
        """This method registers a new tuple in the object's already available.

        Args:
            new_tup (tuple): New tuple to register. 
        """
        # sanity check
        if not isinstance(new_tup, tuple) or not new_tup: # either not tuple or empty tuple 
            raise ValueError(f"Can't add {new_tup} of type {type(new_tup)} to already available tuples")
        # sorting new tuple
        new_tup = tuple(sorted(new_tup))
        # adding new tuple to those already observed
        self.tuples = (self.tuples, new_tup)
        for item in new_tup: 
                self.add(item)

class Problem: 
    def __init__(self, N:int, seed:int=None):
        self.N = N 
        self.P = problem(N = N, seed = seed)
        self.goal = set(range(N))
    
    def is_solvable(self)->bool: 
        """This function returns a boolean corresponding to the result of a test performed to conclude whether or not the
        problem considered is solvable.

        Returns:
            bool: Whether or not the problem is solvable.
        """
        uniques = set()
        for sublist in self.P: 
            uniques.update(sublist)
        if uniques == self.goal: 
            return True
        else: 
            return False
    
    def test_candidate(self, candidate:TupleSet)->bool: 
        """This function returns a boolean correspoding to the test performed to conclude whether or not a given candidate
        can be considered a solution.

        Args:
            candidate (TupleSet): Object used to keep track of the states. 

        Returns:
            bool: Whether or not the given candidate can be considered a solution or not.
        """
        # unique value so far probed are stored as key of TupleSet's counter. 
        uniques_candidate = set(candidate.count.keys())
        if uniques_candidate == self.goal: 
            return True
        else: 
            return False
    
    def compute_cost(self, candidate:TupleSet)->int: 
        """This function computes the cost associated to a given candidate solution as per problem specifications.

        Args:
            candidate (TupleSet): Object used to keep track of the states. 

        Returns:
            int: Cost associated to the given candidate solution.
        """
        return sum(candidate.count.values())
    
    def possible_actions(self, candidate:TupleSet)->Generator: 
        """This function returns the possible actions given a candidate solution.

        Args:
            candidate (TupleSet): Object used to keep track of the states. 

        Yields:
            Generator: Available actions.
        """

        return [
            subtuple for subtuple in tuple(map(lambda arg: tuple(sorted(arg)), self.P)) 
            if subtuple not in map(lambda arg: tuple(sorted(arg)), candidate.tuples)
        ]