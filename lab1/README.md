# Lab1 - Set Covering
This repo contains the solution to the first laboratory of the 2022/2023 Computational Intelligence course called **Set Covering**. The problem specifications can be found [at this link](https://github.com/squillero/computational-intelligence/blob/master/2022-23/lab1_set-covering.ipynb)

## Authors
The contributors of this repo are:
* Francesco Capuano, s295366 
* Matteo Matteotti, s294552  

## Sources 
Part of the code was reproduced from what seen in class, especially from the solution to the [3x3 puzzle problem](https://github.com/squillero/computational-intelligence/blob/master/2022-23/8-puzzle.ipynb).
Another main source from which we yanked is Stack Overflow.

## Methodology
To solve the problem, we turned the unhashable class `MultiSet()` into a custom hashable class called `TupleSet()`. This class is endowed with the `register_new` method, which adds a new tuple to the ones already present (inplace), and the `result` method, which applies a specific action to a state and return the resulting tuple.  
The objects we used are meant to retrieve the set of candidate solutions starting from a state, the cost associated to each candidate solution, and the possible actions given the set of candidate solutions. 


## Notes
Due to Alta Scuola Politecnica committments (mandatory in-presence winter school in Loano) that kept both of us away from Turin from Monday morning until Friday afternoon, we had only been able to implement **breadth-first search** for 17/10's deadline. We plan on further expanding the set of priority functions implemented in our script. 

## Reproduce our results
Once the random seed is fixed to 42, to reproduce our results is sufficient to type in the command line: 

```bash
python3 solution.py
```

## Results
| **problem size** | **solution's cost** | **number of visited nodes** |
|:---:|:---:|:---:|
| **5** | 10 | 45 |
| **10** | 16 | 330 |
| **20** | 24 | 398 |
| **50** | 42 | 4454 |
| **100** | 28 | 5966 |
| **500** | 32 | 28930 |