# Models and tools for Energy System Optimization
This repo is a collection of (MILP) models and other tools for mathematical optimization methods in the field of energy systems.

### Content

- [Models](./README.md#models)
- [Useful tools](./README.md#usefultools)
- [Documentation](./README.md#documentation)

## Models

Some Python code:


### Basic model
`Basic_Model` is a basic optimization model together the pre-processing and post-processing workflow in Python.

### Type day clustering


### Discrete sizing
```
# Purchase decision binary variables (1 if device is installed, 0 otherwise)
x = {}
for device in devs.keys():
    x[device] = {}
    for comp in range(number_comp[device]):
        x[device][comp] = model.addVar(vtype="B", name="x_" + str(device) + "_comp" + str(comp))
```

### Part load efficiency (piece-wise function) 
```python
# CONNECT ENERGY-OUTPUT TO ENERGY-INPUT for every energy conversion system
# Linearization of part-load behavior
if partLoad == 1:
    for device in ["BOI","CHP"]:
        for comp in range(number_comp[device]):
            for t in time_steps:
                model.addConstr(q_flow[device][comp][t] == sum(lin[device][comp][t][i] * devs[device][comp]["q"][i]
                                                     for i in range(number_nodes[device][comp])))
                model.addConstr(g_flow[device][comp][t] == sum(lin[device][comp][t][i] * devs[device][comp]["g"][i]
                                                     for i in range(number_nodes[device][comp])))

                model.addConstr(y[device][comp][t] == sum(lin[device][comp][t][i] for i in range(number_nodes[device][comp])))
                model.addSOS(gp.GRB.SOS_TYPE2, [lin[device][comp][t][i] for i in range(number_nodes[device][comp])])

    for device in ["CHP"]:
        for comp in range(number_comp[device]):
            for t in time_steps:
                model.addConstr(el_flow[device][comp][t] == sum(lin[device][comp][t][i] * devs[device][comp]["el"][i]
                                                     for i in range(number_nodes[device][comp])), "electrical_power_" + str(device) + "_comp" + str(comp) + "_t" + str(t))
```
BOI als Beispiel, AbbildungsDoku mit Diagramm, Kurzergebnisse (Vergleich zu konstantem eta)

### Piece-wise linear investment 
TES als Beispiel, 

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

## Useful tools
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

### Contact
Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen Unviersity, Germany [(contact)](http://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team6/~poet/Wirtz-Marco/?allou=1&lidx=1)

