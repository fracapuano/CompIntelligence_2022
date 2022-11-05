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
class Problem: 
    def __init__(self, N:int, seed:int=None):
        self.N = N 
        self.P = np.array(problem(N = N, seed = seed))
        self.seed = seed
        self.goal = set(range(N))

        self.fitness_calls = 0
        self.max_reps_cost = len(list(chain.from_iterable(self.P)))
    
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
    
    def return_candidate(self, candidate:List[bool])->List[list]: 
        """This function returns the actual candidate in P-space corresponding to the boolean mask in input `candidate`.

        Args:
            candidate (List[bool]): List of booleans in which each element is True if the corresponding list in P is chosen, 0 otherwise.

        Returns:
            List[list]: P masked with respect to candidate.
        """
        return self.P[candidate]

    def test_candidate(self, candidate:List[bool])->bool: 
        """This function returns a boolean correspoding to the test performed to conclude whether or not a given candidate
        can be considered a solution.

        Args:
            candidate (np.array): Array used to define a single candidate solution. 

        Returns:
            bool: Whether or not the given candidate can be considered a solution or not.
        """
        # retrieve actual candidate
        actual_candidate = self.return_candidate(candidate=candidate)
        # unique values in sub-P
        uniques_candidate = set(chain.from_iterable(actual_candidate))
        if uniques_candidate == self.goal: 
            return True
        else: 
            return False
    
    def fitness(self, candidate:List[bool])->float: 
        """This function computes the cost associated to a given candidate solution as per problem specifications.

        Args:
            candidate (Candidate): Object used to keep track of the states. 

        Returns:
            float: Cost associated to the given candidate solution.
        """
        # incrementing fitness calls
        self.fitness_calls += 1
        # retrieve actual candidate
        actual_candidate = self.return_candidate(candidate=candidate)
        # unique values in sub-P
        uniques_candidate = set(chain.from_iterable(actual_candidate))
        # True (1) when a number is both in goal and uniques_candidate, False (0) otherwise, used to measure fitness in its `covering` dimension.
        covering_fitness = sum([integer in uniques_candidate for integer in self.goal])
        # Repetitions fitness (decreasing as number of duplicates increases)
        reps_fitness = len(list(chain.from_iterable(actual_candidate)))
        # normalizing both fitness indicators in 0-1
        covering_fitness /= self.N
        reps_fitness /= self.max_reps_cost
        
        return covering_fitness - 2 * reps_fitness
class Genetics:
    def __init__(
        self, 
        genetic_pool,
        Mu:int=20,
        Lambda:int=40,
        mutation_probability:float=0.7, 
        cross_probability:float=0.5
        ):
        
        self.Mu = Mu; self.Lambda = Lambda
        
        self.mut = mutation_probability
        self.cross_p = cross_probability
        self.genetic_pool = genetic_pool
    
    def recombination(self, parents:List[List[bool]])->List[bool]: 
        """This function recombines parents to obtain a child defined as a mixture of the two parents.

        Args:
            parents (List[List[Candidate]]): List of parents to be considered in their List[bool] representation.

        Returns:
            List[bool]: Offspring obtained as a combination of the parents. 
        """
        if len(parents) != 2: 
            raise NotImplementedError("Recombination for n != 2 has not been implemented yet")
        
        parent1, parent2 = parents
        return [p1_gene if realization > self.cross_p else p2_gene for p1_gene, p2_gene, realization in zip(parent1, parent2, np.random.random(size=len(parent1)))]
        
    def mutation(self, individual:List[bool])->List[bool]:
        """This function mutates the candidate individual according to a given mutation probability.

        Args:
            individual (List[bool]): Given individual considered.

        Returns:
            List[bool]: New candidate obtained mutating a given individual.
        """
        mutant = individual.copy()
        for idx, gene in enumerate(individual):
            # randomly chose whether or not to change a given element
            if random.random() < self.mut:
                # replace gene at position idx with its boolean opposite (through `~`)
                mutant[idx] = ~gene
        return mutant
     
    def generate_offspring(self, parents:List[List[bool]]) -> List[List[bool]]:
        """This function returns a population of individual obtained from parents.

        Returns:
            list: Population obtained from parent1 and parent2.
        """
        return [self.mutation(self.recombination(parents)) for _ in range(self.Lambda)]
    