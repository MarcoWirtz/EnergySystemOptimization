# Models and tools for Energy System Optimization
This repo is a collection of (MILP) models and other tools for mathematical optimization methods in the field of energy systems.

### Content

- [Overview](./README.md#overview)
- [Features](./README.md#features)
- [Instructions](./README.md#instructions)
- [Documentation](./README.md#documentation)
- [References](./README.md#references)

### News
    01-Jul-2018: Preparing the switch to Julia 0.7 and to the new version of JuMP 
    
### Feedback
All bugs, feature requests, pull requests and feedback are welcome. 
In brief, every contributions aiming to share our efforts, our algorithms, our productions around this open source software are welcome.

### Coordinator
Marco Wirtz, Institute of Indoor Climate and Energy..., RWTH Aachen Unviersity, Germany [(contact)](http://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team6/~poet/Wirtz-Marco/?allou=1&lidx=1)

## Overview

### Aims
- Solver of multiobjective linear optimization problems for scientifics and practionners
- Easy to formulate a problem, to provide data, to solve a problem, to collect the outputs, to analyze the solutions
- Natural and intuitive use for mathematicians, informaticians, engineers

### Purposes
- Solving needs: methods and algorithms for performing numerical experiments
- Research needs: support and primitives for the development of new algorithms
- Pedagogic needs: environment for practicing of theories and algorithms

### Characteristics
- Efficient, flexible, evolutive solver
- Free, open source, multi-platform, reusing existing specifications
- Easy installation, no need of being expert in computer science

### Background
- Julia programming language [(link)](http://julialang.org/)
- JuMP algebraic language [(link)](http://www.juliaopt.org/JuMP.jl/0.18/)
- Usual free (GLPK, Clp/Cbc) and commercial (CPLEX, GUROBI) MILP solvers

## ...
- vOptGeneric: Multiobjective non-structured problems / algebraic language (JuMP),
    -  LP: Linear Program
    -  MILP: Mixed Integer Linear Program
    -  ILP: Integer Linear Program 
    -  Forthcoming: [MKP, UDFLP, SSCFLP, CFLP, PATHS]

### Inputs
- Non-structured problems: 
    - direct with the provided languages (Julia, JuMP)
    - standard MOP format (ILP, MILP, LP)
    - specific problem format (MILP)
- Structured problems: 
    -  direct with the language (Julia), 
    -  specific problem format (2LAP, 2UKP, 2UFLP)

### Outputs
- Non-structured problems: 
    - standard 2MOP format (ILP, MILP, LP)
- Structured problems: 
    - specific problem format (2LAP, 2UKP, 2UFLP)

## Instructions 

### Information
- ... models are tested with Pyhton X.X, Gurobi version X.X.
- Required python packages: ...

### Installation and usage Instructions
Refer to the instructions provided for
- [vOptSpecific](https://github.com/vOptSolver/vOptSpecific.jl)
- [vOptGeneric](https://github.com/vOptSolver/vOptGeneric.jl)


## Documentation
- Tutorials: Python installation
- Presentations given in conferences [(folder talks)](https://github.com/MarcoWirtz)


## References

-   [Majewski2016] L.G. Chalmet, L. Lemonidis, D.J. Elzinga: 
    An algorithm for the bi-criterion integer programming problem.
    *European Journal of Operational Research*, Volume 25, Issue 2, Pages 292-300, 1986.

---

Terms and acronyms used
- LP: Linear Program
- MILP: Mixed Integer Linear Program
- IP: Integer linear program
- GUROBI: a commercial solver

