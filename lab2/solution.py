from lab_utils import *
from collections import Counter
import matplotlib.pyplot as plt
import time
from typing import List, Tuple
from tqdm import tqdm
import os
import glob
import argparse

def parse_args()->None: 
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-evolution", default=False, type=bool, help="Whether or not to save the whole training process")
    parser.add_argument("--max-generations", default=100, type=int, help="Maximal number of generations")
    parser.add_argument("--visualize-opt", default=True, type=bool, help="Whether or not to save an image visualizing the evolution process")
    parser.add_argument("--clear-past", default=True, type=bool, help="Whether or not to empty routes and images content before optimization")
    return parser.parse_args()

args = parse_args()

class Solution: 
    def __init__(
        self, 
        N:int,
        population_size:int,
        offspring_size:int,
        tournament_size:int=10,
        mutant_loci:int=1,
        cross_probability:float=0.5,
        seed:int = None):

        self.population_size = population_size; self.offspring_size = offspring_size
        self.problem = Problem(N = N, seed = seed)
        self.genetics = Genetics(
            Mu = population_size, 
            Lambda = offspring_size, 
            mutant_loci = mutant_loci
            
            )
        self.tournament_size = tournament_size
        self.cross_probability = cross_probability
        self.recombinations = list()

        # initial population
        self.population = [(np.random.choice([0, 1], size = len(self.problem.P)).tolist()) for _ in range(self.population_size)]

    def obtain_parents(self, n_parents:int=2)->List: 
        """This function returns n_parents obtained from n_parents-tournaments of size tounrnamentsize according to their fitness value.

        Args:
            n_parents (int, optional): Number of parents to be obtained from different tournaments. Defaults to 2.

        Returns:
            List: List of parents
        """
        parents = list()
        for _ in range(n_parents): 
            tournament = random.sample(self.population, k = self.tournament_size)
            parents.append(
                sorted(tournament, key=lambda candidate: self.problem.fitness(candidate), reverse=True)[0] # selecting the fittest candidate in tournament 
            )
        return parents
    
    def generate_offspring(self)->List:
        """This function generates offspring_size individuals.

        Returns:
            List: Offspring.
        """
        offspring = list()
        recombinations = 0

        for _ in range(self.offspring_size): 
            # obtaining parents in the current population
            parents = self.obtain_parents()
            # whether or not to generate an individual mutating a parent or recombinating them.
            if random.random() < self.cross_probability: # do recombination 
                recombinations += 1
                individual = self.genetics.recombination(parents = parents)
            else: # do mutation
                parent = random.sample(parents, k = 1)[0]
                individual = self.genetics.mutation(parent)
            offspring.append(individual)
        # storing the number of recombinant individuals in offspring
        self.recombinations.append(recombinations)
        return offspring

    def evolve(
        self,
        strategy:str="comma",
        n_loci:int=1, 
        max_generations:int=1_000) -> Tuple[List, List]:
        """This function performs a Genetic Algorithm using computational evolution to solve a given problem.

        Args:
            tournament_size (int, optional): Size of the subsets of population in which parents are selected. Defaults to 5.
            strategy (str, optional): Wheter to perform (mu/rho, lambda) strategy or (mu/rho + lambda). Defaults to "comma".
            n_loc (int, optional): Number of loci to mutate in mutation. Defaults to 1.
            max_generations (int, optional): Maximal Number of generations considered. Defaults to 1_000.

        Raises:
            ValueError: Raises an error if strategy is not "comma" or "plus".

        Returns:
            Tuple[List, List]: Best candidate after max_generations and history of fittest individuals' fit.
        """
        if strategy.lower() not in ["comma", "plus"]: 
            raise ValueError('Strategy must be one of ["comma", "plus"]!')
        
        # update number of mutant loci
        self.genetics.mutant_loci = n_loci

        history, fittest = list(), list()

        for _ in (pbar := tqdm(range(max_generations))):
            offspring = self.generate_offspring()

            if strategy.lower() == "comma": 
                # self.population =  # getting rid of all elements in past population
                self.population = (
                    sorted(offspring, key=lambda candidate: self.problem.fitness(candidate), reverse=True)[:self.population_size] # add best elements of offspring
                )
            else: # "plus" strategy
                self.population += offspring # add offspring to population
                # keep only best elements from new enlarged population
                self.population = sorted(self.population, key=lambda candidate: self.problem.fitness(candidate), reverse=True)[:self.population_size]
            
            fittest.append(self.population[0]) # storing fittest individual
            history.append(self.problem.fitness(self.population[0])) # storing fitness of fittest (1st) individual in population
            pbar.set_description(f"Fitness value: {history[-1]}")

        self.fittest_individuals = fittest
        return self.population[0], history

def main(): 
    problem_size = [5, 10, 20, 50, 100, 500]

    if args.clear_past:
        folders = ["./images", "./routes"]
        for folder in folders: 
            files = os.listdir(folder)
            for file in files: 
                os.remove(folder + "/" + file)
    
    for size in problem_size:
        pop_size = 20; off_size = int(1.5 * pop_size); tournament_size = pop_size // 3
        
        s = Solution(
            N = size, 
            seed = 42, 
            population_size = pop_size, 
            offspring_size = off_size, 
            tournament_size = tournament_size, 
            cross_probability=0.7
            )

        if not s.problem.is_solvable(): 
            raise Exception("Problem is not solvable!")
            continue
        
        max_generations = args.max_generations
        save_evolution = args.save_evolution

        initial_time = time.time()
        result, history = s.evolve(max_generations=max_generations, strategy="plus")
        solution_time = time.time() - initial_time

        if save_evolution: 
            fittest_individuals = np.array(s.fittest_individuals)
            fittest_fit = np.array(history).reshape(-1,1)
            evolution = np.hstack(
                (fittest_individuals, fittest_fit)
            )

            np.savetxt(f"routes/N={size}-fittest_individuals.txt", evolution)
        
        print(f"For problem size: {size}")
        print(f"In {len(history)}/{max_generations} generation a {'valid' if s.problem.test_candidate(result) else 'non-valid'} solution has been found!")
        print(f"The cost of said solution is: {sum(Counter(chain.from_iterable(s.problem.return_candidate(result))).values())}.")
        print()
        print(f"Elapsed in: {solution_time} (s)")
        print("-"*50)

        if args.visualize_opt: 
            fig, ax = plt.subplots()
            ax.plot(history, lw = 2, alpha = .5)
            ax.scatter(np.arange(len(history)), history, marker = "x", c = "grey", s = 25)
            ax.set_title(f"Set Covering - N = {size} \nFitness in iterations", fontweight = "bold")
            ax.set_xlabel("Generations", fontsize=12)
            ax.set_ylabel("Fitness of Fittest Individual", fontsize=12)

            fig.savefig(f"images/N={size}-fitness.svg")

if __name__ == "__main__": 
    main()