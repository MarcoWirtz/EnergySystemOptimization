# Models and tools for Energy System Optimization
This repo is a collection of (MILP) models and other tools for mathematical optimization methods in the field of energy systems.

### Content

- [Models](./README.md#models)
- [Documentation](./README.md#documentation)

## Models

Some Python code:
```python
s = "Python syntax highlighting"
print s
```

### Basic model
`Basic_Model` is a basic optimization model together the pre-processing and post-processing workflow in Python.

### Type day clustering


### Discrete sizing


### Part load efficiency


## Visualization

As a result of the optimization workflow four files are created:
- All decision variables are saved in `model.sol` (created by Gurobi)
- All parameter regarding the technologies (efficiency, investment, etc.) are saved in `parameter_dev.json`
- All further parameter (interest rate, costs for natural gas, ...) are saved in `parameter.txt`
- Demand time series are saved in `demands.txt`

The visualization methods presented below use these output files to create illustrative plots to visualize and analyse the numeric results. 

### Hourly time steps of complete year (8760 time steps)

#### Yearly plot (averaged over months) (1 plot)
#### Monthly plot (averaged over days) (12 plots)
#### Daily plot (365 plots)
#### Carpet plot
#### Box plot (daily profile)
#### Box plot (seasonal profile)

### Type days
#### Visualization method 1
#### Visualization method 2
#### Visualization method 3

### Others
#### Scatter density plot
#### Matrix illustration

## Further tools
### Gurobi solver tuning


---

## Documentation 

### Installation and usage Instructions
- ... models are tested with Pyhton X.X, Gurobi version X.X.
- Required python packages: ...

---

### Other
    Example Text

### Feedback
All bugs, feature requests and feedback are welcome.

### Coordinator
Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen Unviersity, Germany [(contact)](http://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team6/~poet/Wirtz-Marco/?allou=1&lidx=1)

