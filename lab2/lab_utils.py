from collections import Counter
import random
from re import I
from typing import Generator, List
from itertools import chain
import numpy as np

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

class Candidate: 
    def __init__(self, data:list): 
        self.data = data
    
    def obtain_count(self): 
        """This function counts the number of occurrences of each item in data.
        """
        # initialize counter
        self.count = Counter()
        # storing the counter associated to each number
        if self.data:
            for item in chain(self.data): 
                self.add(item)

    def add(self, item, *, cnt=1):
        """This function updates the counter associated to the solution. 

        Args:
            item (_type_): Number to be considered for the update.
            cnt (int, optional): How much to update the counter by. Defaults to 1.
        """
        assert cnt >= 0, "Can't add a negative number of elements"
        if cnt > 0:
            self.count[item] += cnt
    
    def action(self, sublist:list, update_counter:bool=True)->None: 
        """This method registers a new sublist in the object's data attribute.

        Args:
            sublist (list): New sublist to register inside the solution. 
            update_counter (bool, optional): Whether or not to update the object's counter. Defaults to True.
        """
        # sanity check
        if not isinstance(sublist, list) or not sublist: # either not a list or an empty list
            raise ValueError(f"Can't modify the candidate with {sublist} of type {type(sublist)}.")
        # append new sublist
        self.data.append(sublist)

        if update_counter: 
            self.obtain_count()
    
    def remove_element(self, index:int, update_counter:bool=True)->None: 
        """This function removes the sublist in data in the position index.

        Args:
            index (int): Index at which to remove the point.
            update_counter (bool, optional): Whether or not to update the object's counter. Defaults to True.
        """
        self.data.pop(index=index)

        if update_counter: 
            self.obtain_count()

class Problem: 
    def __init__(self, N:int, seed:int=None):
        self.N = N 
        self.P = problem(N = N, seed = seed)
        self.seed = seed
        self.goal = set(range(N))

        self.fitness_calls = 0
    
    def max_repetitions_cost(self): 
        """This function computes the value of the maximal cost deriving from repetitions of elements in P.
        """
        return len(chain(self.P))

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
    
    def test_candidate(self, candidate:Candidate)->bool: 
        """This function returns a boolean correspoding to the test performed to conclude whether or not a given candidate
        can be considered a solution.

        Args:
            candidate (Candidate): Object used to define a single candidate. 

        Returns:
            bool: Whether or not the given candidate can be considered a solution or not.
        """
        # unique value so far probed are stored as key of TupleSet's counter. 
        uniques_candidate = set(candidate.count.keys())
        if uniques_candidate == self.goal: 
            return True
        else: 
            return False
    
    def fitness(self, candidate:Candidate)->float: 
        """This function computes the cost associated to a given candidate solution as per problem specifications.

        Args:
            candidate (Candidate): Object used to keep track of the states. 

        Returns:
            float: Cost associated to the given candidate solution.
        """
        # incrementing fitness calls
        self.fitness_calls += 1
        # True (1) when a number is both in goal and candidate values, False (0) otherwise - to measure fitness 
        covering_fitness = sum([integer in candidate.count.keys() for integer in self.goal])
        # Repetitions fitness (decreasing as number of duplicates increases)
        reps_fitness = sum(candidate.count.values())
        # normalizing both fitness indicators in 0-1
        covering_fitness /= self.N
        reps_fitness /= self.max_repetitions_cost()
        
        return covering_fitness - reps_fitness

class Genetics:
    def __init__(
        self, 
        genetic_pool,
        pop_size:int=20,
        mutation_probability:float=0.7, 
        cross_probability:float=0.5
        ):
        
        self.pop_size = pop_size
        self.mut = mutation_probability
        self.cross_p = cross_probability
        self.genetic_pool = genetic_pool
    
    def recombination(self, parents:List[Candidate])->Candidate: 
        """This function recombines parents to obtain a child defined as a mixture of the two parents.

        Args:
            parents (List[Candidate]): List of parents to be considered.

        Returns:
            Candidate: Offspring obtained as a combination of the parents. 
        """
        if len(parents) != 2: 
            raise NotImplementedError("Recombination for n != 2 has not been implemented yet")
        
        parent1, parent2 = parents
        return [p1_gene if realization > self.cross_p else p2_gene for p1_gene, p2_gene, realization in zip(parent1, parent2, np.random.random(size=len(parent1)))]
        
    def mutation(self, individual:Candidate)->Candidate:
        """This function mutates the candidate individual according to a given mutation probability.

        Args:
            individual (Candidate): Given individual considered.
            genetic_pool (list): List of possible elements that can be added to current candidate.

        Returns:
            Candidate: New candidate obtained mutating a given individual.
        """
        mutant = individual.copy()
        for idx, _ in enumerate(individual):
            # randomly chose whether or not to change a given element
            if random.random() < self.mut: 
                # replace gene at position idx with randomly chosen gene from genetic_pool
                mutant[idx] = random.choice(self.genetic_pool)
        return mutant
     
    def generate_offspring(self, parent1:Candidate, parent2:Candidate) -> list: 
        """This function returns a population of individual obtained from parent1 and parent2.

        Returns:
            list: Population obtained from parent1 and parent2.
        """
        return [self.mutation(self.recombination(parent1, parent2)) for _ in range(self.pop_size)]
    