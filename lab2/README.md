# Lab2 - Set Covering with evolutionary algorithms
This repo contains the solution to the second laboratory of the 2022/2023 Computational Intelligence. The problem specifications can be found [at this link](https://github.com/squillero/computational-intelligence/blob/master/2022-23/lab1_set-covering.ipynb). To address the problem, we used an evolutionary algorithm, as opposed to the search algorithms used during the first laboratory. 
## Authors
The contributors of this repo are:
* [Francesco Capuano](https://github.com/fracapuano/CompIntelligence_2022), s295366 
* [Matteo Matteotti](https://github.com/mttmtt31/compIntelligence_2022), s294552  

## Sources 
This solution mainly stems from the resolution of the [one-max problem](https://github.com/squillero/computational-intelligence/blob/master/2022-23/one-max.ipynb).

## Methodology
### Problem encoding
To better encode the problem, we represented each candidate as an array of integers in the space $\mathbb{R}^{\vert P \vert}$, according to the definition of $P$ given in the [problem specification](https://github.com/squillero/computational-intelligence/blob/master/2022-23/lab1_set-covering.ipynb).

Each candidate $x$ was defined as:

$$
x_i = 
\begin{cases}
1 & \text{ if } P_i \text{ is chosen } \\
0 & \text{ otherwise}
\end{cases}
$$
### Fitness of a candidate
Our methodology is strongly based on the definition of **fitness** of a given candidate, which has been slightly modified compared to what has been seen in class. 

Specifically, given a candidate, the `fitness()` function returns a float, evaluated as a weighted difference between the coverage of that candidate (*i.e.*, the proportion of the N digits are actually covered) and the bloat (*i.e.*, the total number of digits inside the candidate, min-max normalised), normalised between 0 and 1.

In particular, considering that we observed that the problem was solved in its "covering" dimension pretty easily by our approach (i.e., candidates were covering the whole range $1: N-1$), we chose weights penalizing more the bloat. What our approach struggled the most with, was identifying solutions with a reduced cost, hence our choice of using weights such as: 

1. $w_{covering} = 0.2$
2. $w_{bloat} = 0.8$

Once these weights were available, we obtained the fitness value using the following formula: 

$$
\begin{equation*}
(w_{covering} \cdot \text{covering\_fitness} + w_{bloat} \cdot \text{reps\_fitness)} - w_{bloat} \in [0, 1]
\end{equation*}
$$

Since we previously scaled both $covering\_fitness$ and $reps\_fitness$ in the respective 0-1 range, this formulation of each individual fitness granted us values in the 0-1 range, which played a major role in the diagnostic of our solution, as each individual's fitness had a clear and direct interpretation.

### The evolution
Our method evolves through a given number of generations. 
We implemented two different strategies: `comma`, which corresponds to the $(\mu/\rho, \lambda)$-strategy and `plus`, which corresponds to the $(\mu/\rho + \lambda)$-strategy.

A generation is defined as follows.

  1. **parents selection**: first, a subset of the total population of size `population_size` (*i.e.*, $\mu$) drawn. A further subset of size `tournament_size`  is drawn into a tournament, which returns the 2 fittest candidate, *i.e.*, the parents.
  2. **offspring generation**: the offspring is generated either as a random recombination (with probability `cross_probability`) of the two selected parents or as a random mutation of either parent. Specifically, a parent's random **mutation** considers the opposite gene in a locus, *i.e.*, considers the opposite of one entry in the encoded problem. This process is repeated ``offspring_size`` (*i.e.*, $\lambda$) times.
  3. **survival selection**: performed according to the strategy. If `comma`, only the best $\mu$ offspring's individuals are kept and become the new population. If `plus`, the offspring is entirely added to the population and only the best $\mu$ individuals are kept.

## Reproduce our results
To reproduce our results, set the seed to 42, and use the following values of hyperparameters:

| **hyperparameter** | **value** 
|:---:|:---:
| `population_size` | 20
| `offspring_size` | 30
| `cross_probability` | 0.7
| `tournament_size` | 6
| `max_generations` | 1000
| `strategy`| $\mu/\rho + \lambda$

Once the random seed is fixed to 42, to reproduce our results is sufficient to type in the command line: 

```bash
python3 solution.py
```

It is possible to modify the number of generations that the algorithm is allowed to use to converge to better solutions and visualize/save the optimization process, both for what concerns the actual fittest individuals across generations and their fitness value. 

In particular, the following arguments can be used to modify the execution of the script: 

1. `max-generations`: Maximal number of generations.
2. `visualize-opt`: Whether or not to save an image visualizing the evolution process.
3. `clear-past`: Whether or not to empty routes and images content before optimization.
4. `save-evolution`: Whether or not to save the whole training process.

To fully reproduce our results, saving only the optimization output and disregarding the individuals it is sufficient to type in command line: 

```bash
python3 solution.py --max-generations 1000
```

## Results
| **problem size** | **solution's cost** | **time elapsed (s)** |
|:---:|:---:|:---:|
| **5** | 5 | 9.13 |
| **10** | 15 | 11.18 |
| **20** | 20 | 7.14 |
| **50** | 101 | 17.54 |
| **100** | 230 | 34.48 |
| **500** | 10398 | 729.99 |
| **1000** | 163173 | 4802.42 |

Our results can also be visualized for what concerns the number evolution of the population along generations. It is possible to see that in the 1000 generations allowed, the majority of the problem sizes converged passing the elbow point (after which the relative improvement of the fittest individual could be considered marginal). 

| | | |
|:-------------------------:|:-------------------------:|:-------------------------:|
|![img](images/N%3D5-fitness.svg)|![img](images/N%3D10-fitness.svg)|![img](images/N%3D20-fitness.svg)|
|![img](images/N=50-fitness.svg)|![img](images/N%3D100-fitness.svg)|![img](images/N=500-fitness.svg)|

From this standpoint it is also possible to see that the very large cost associated to the problem size `N=500` is mainly due to the fact that the number of generations was probably to small to allow the population to increase its fitness value. 

To obtain satisfactory results (in terms of actual cost) of our solution, we carried out an extra optimization-route consisting of 10k generations for the two values of `N` that we struggled to solve in the first place. 

The resutls of this extra run are presented below.

| **problem size** | **solution's cost** | **time elapsed (s)** |
|:---:|:---:|:---:|
| **500** | 1847 | 1597.25 |
| **1000** | 4232 | 7092.64 |

The two optimization routes are presented in the following picture. 
| | |
|:-------------------------:|:-------------------------:|
|![img](images/N%3D500-fitness-10k.svg)|![img](images/N%3D1000-fitness.svg)