import random
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
        self.P = np.array(problem(N = N, seed = seed), dtype=object)
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
        return self.P[[bool(ind) for ind in candidate]]

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
    
    def fitness(self, candidate:List[bool], weights:list = [0.2, 0.8])->float: 
        """This function computes the fitness of a given candidate solution as per problem specifications.
        In particular, the fitness is normalized in the 0-1 range and obtained penalizing more 
        the repetitions than the non-coverage of certain numbers. 


        Args:
            candidate (Candidate): Object used to keep track of the states. 
            weights (list, optional): Weights to be used to combine the two fitness indicators. 
                                      Defaults to [0.2, 0.8]

        Returns:
            float: Cost associated to the given candidate solution.
        """
        # incrementing fitness calls
        self.fitness_calls += 1
        # w_reps must be negative since repetitions are penalized
        w_coverage, w_reps = weights; w_reps *= -1
        # retrieve actual candidate
        actual_candidate = self.return_candidate(candidate=candidate)
        # unique values in sub-P
        uniques_candidate = set(chain.from_iterable(actual_candidate))
        # number of distinct numbers is a measure of fitness in its `covering` dimension
        covering_fitness = len(uniques_candidate)
        # Repetitions fitness (decreasing as number of duplicates increases)
        reps_fitness = len(list(chain.from_iterable(actual_candidate)))
        # normalizing both fitness indicators in 0-1
        covering_fitness = (covering_fitness - 1) / (self.N - 1)
        reps_fitness =  (reps_fitness - self.N)/(self.max_reps_cost - self.N)
        
        # normalizing in the 0-1 range through min-max normalization
        return (w_coverage * covering_fitness + w_reps * reps_fitness) - w_reps

class Genetics:
    def __init__(
        self, 
        Mu:int=20,
        Lambda:int=40,
        mutant_loci:int=1,
        ):
        
        self.Mu = Mu; self.Lambda = Lambda
        self.mutant_loci = mutant_loci
            
    def recombination(self, parents:List)->List[bool]: 
        """This function recombines parents to obtain a child defined as a mixture of the two parents.

        Args:
            parents (List[List[Candidate]]): List of parents to be considered in their List[bool] representation.

        Returns:
            List[bool]: Offspring obtained as a combination of the parents. 
        """
        if len(parents) != 2: 
            raise NotImplementedError("Recombination for n != 2 has not been implemented yet")
        # mapping parents to array
        parent1, parent2 = list(map(lambda parent: np.array(parent, dtype=object), parents))
        # randomly sampling a scalar to be used to cut-and-cross the two parents
        recombination = np.random.random()
        # performing recombination
        recombined = np.hstack(
            (
                parent1[:int(recombination*len(parent1))], # up to recombination "index"
                parent2[int(recombination*len(parent2)):]) # from recombiantion "index" onwards
        )
        return recombined.tolist()

    def mutation(self, individual:List)->List[int]: 
        """This function mutates n_loci of the candidate individual's genome.

        Args:
            individual (List): Given individual considered.

        Returns:
            List[int]: New candidate obtained mutating a given individual.
        """
        # for _ in range(self.mutant_loci): 
        # sampling the index at which to perform mutation
        mutant_index = np.random.randint(low = 0, high = len(individual))
        # mutation (flip of 1 to 0 and viceversa) is obtained using XOR operator
        individual[mutant_index] = individual[mutant_index] ^ 1

        return individual
    