# Models and tools for Energy System Optimization
This repo is a collection of typical modelling approaches frequently used for Mixed-Interger Linear Programming (MILP) formulations in the field of designing energy supply systems.

### Content

- [Example MILP model](./README.md#models)
- [Modeling approaches](./README.md#models)
- [Useful tools](./README.md#useful-tools)
- [Documentation](./README.md#documentation)

## Example MILP model
In the folder `Basic_Model` is a basic optimization model written in Python/Gurobi along with its pre-processing and post-processing routines. You can download it and run the file `run_multi_objective.py`.

As a result of the optimization workflow four files are created:
- All decision variables are saved in `model.sol` (created by Gurobi)
- All parameter regarding the technologies (efficiency, investment, etc.) are saved in `parameter_dev.json`
- All further parameter (interest rate, costs for natural gas, ...) are saved in `parameter.txt`
- Demand time series are saved in `demands.txt`

The visualization functions in `post_processing.py` use these output files to create illustrative plots to visualize and analyze the numeric results. These plots include 12 monthly plots (averaged over days), 365 daily plots, carpet plots for every technology, box plots which show the seasonal and daily profile.  

Furthermore the matrix of the (relaxed) MILP problem can be displayed. This looks like this:
<img src="https://github.com/MarcoWirtz/EnergySystemOptimization/blob/master/images/LP_matrix.png" width="400">

The code is tested with Pyhton 3.6 and Gurobi version 7.5.1.

## Modeling approaches 
Different MILP formulations has been presented in scientific literature. A few model variations are presented in the following:

### Type day clustering
In energy system simulations and optimizations approaches, often a full year is considered. In many models an hourly time resolution is chosen, which results in 8760 time steps for which steady state conditions are assumed. However, many MILPs are complex and comprise many continuous and binary decision variables for each time step. Therefore, the consideration of all 8760 time steps leads to huge computation times. In order to reduce the computational complexity, often so-called *type days* are introduced. All 365 days of a year are reduced to a smaller number of typical days which represent the entire year. Detailed studies, like [Schütz et al., 2016](https://pdfs.semanticscholar.org/aae0/60d220ca9490c8123abaade3d97ff674c266.pdf) and [Schütz et al., 2018](https://www.sciencedirect.com/science/article/pii/S0960148118306591) investigate the effect of introducing type days in the optimization model. Here, a k-medioids clustering approach is used to cluster 365 days to a specified number of type days. The clustering is done regarding specific time serieses e.g. thermal demands. If renwable energies play an important role within the energy system, weather data has to be considered in the clustering process as well. The clustering process is done during a pre-processing. The clustering process represents a seperate optimization problem, which consists of a large number of binary variables. Therefore, full convergence cannot be realized. However, the problem converges fast and small gaps are reached within a few seconds. [Schütz et al., 2018](https://www.sciencedirect.com/science/article/pii/S0960148118306591) suggest that already a small number of type days (< 20) show good results compared to a full year optimization. However, the number strongly depends on the underlying MILP. The parameter study was conducted for a single-objective optimization (total annualized costs).

### Piece-wise linear investment
One big share of total annualized costs are investment costs of the components. The investment costs of large components usually depend non-linearly with the components size. The cost curve (rated power vs specific costs) can be approximated by piece-wise linear formulation. For this purpos, help variables `lin` for every time step and every supporting point of the piece-wise linear relation are introduced which connect the rated power with the specific costs. The formulation is shown for one component, boiler (BOI), in the following:
```python
lin = {}
    for device in ["BOI"]:   
        lin[device] = {}
        for i in range(len(devs[device]["cap_i"])):
            lin[device][i] = model.addVar(vtype="C", name="lin_" + device + "_i" + str(i))      
```
For the formulation Special Ordered Sets of type 2 (SOS2) are introduced. These are ordered set of non-negative variables, of which at most two can be non-zero, and if two are non-zero these must be consecutive in their ordering. Furthermore, the sum of all help variables for a specific component must be equal to 1. This is expressed by:
```python
for device in ["BOI"]:
    model.addSOS(gp.GRB.SOS_TYPE2, [lin[device][i] for i in range(len(devs[device]["cap_i"]))])
    model.addConstr(sum(lin[device][i] for i in range(len(devs[device]["cap_i"]))) == 1)
```
The rated power of the boiler is expressed by
```python  
for device in ["BOI"]:
    model.addConstr(cap[device] == sum(lin[device][i] * devs[device]["cap_i"][i] for i in range(len(devs[device]["cap_i"]))))
```
The investment costs are expressed by
```python
inv = {}
for device in ["BOI"]:
    inv[device] = sum(lin[device][i] * devs[device]["inv_i"][i] for i in range(len(devs[device]["cap_i"]))) 
```       

### Discrete sizing (questionable)
In some optimization models, the rated power of a device is not modeled as a continuous decision variable. Instead, binary variables are used to describe the purchase decision of discrete devices. Reason for this approach is that in practice devices cannot be purchased with every possible rated power, but only discrete device capacities can be purchased. 
From my point of view, for large energy systems on district scale this aspect can be neglected since it describes a level of detail which cannot hold for other substantial aspects of the optimization model and therefore suggest an apparent accuracy that does not hold for the rest of the optimization model. Therefore, usually continuous variable for the rated power of components is sufficient. Moreover, binary decision variables increase the computation time significantly.
Nevertheless, if only discrete sizing of devices should be taken into account, this can be done as follows:
```python
# Purchase decision binary variables (1 if device is installed, 0 otherwise)
x = {}
for device in devs.keys():
    x[device] = {}
    for comp in range(number_comp[device]):
        x[device][comp] = model.addVar(vtype="B", name="x_" + str(device) + "_comp" + str(comp))
```

### Minimal part load (questionable) 
Energy conversion units normally operated within well-defined load ranges. For example, a combined heat and power unit cannot be operated at 10 % of its rated-power. If the operation of a device is modelled to  In order to model the minimal part-load limits of a technology more accurately, especially one approach often widely found in the literature. In this approach further binary variables are introduced for each time step and each device. Depending on the number of time steps that are considered this leads to a significant increase of the model complexity. As usually `x` represents a binary describing if a device is purchased or not, `y` represents if the technology is activated/operated a specific time step or not. Here, `y=1` presents...

### Part load efficiency (questionable) 
In optimization models the operation of the devices is described in very detailed way. One aspect that is often addressed is part-load behavior of devices. For this purpose, binary variables are introduced. Fact sheets are used to derive piece-wise linear function within  performance charts. Its doubtful whether the detailed description of the operation is really reasonable since there are numerous aspects within the optimization model which have a much higher impact on the results but are modeled with much less detail. Furthermore, usually hourly time steps are employed which also influence the operation. For example, if the optimization result suggest to run an engine for one hour at half load and then shut it down, in practice this could be easily realized by running the engine half an hours at full laod and utilize possible storage capacities (which has been installed anyways). This way of modeling part-load behavior is also expensive from a computation point of view as it requires more than one extra binary variable in every time step. 
Nevertheless, if only part-load behavior should be taken into account, this can be done as follows:
```python
# Linearization of part-load behavior
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

### Further model variations
In scientific literature further formulations has been introduced which try to model the components performance in more detail. These approaches comprise:
- Taking into account start up costs, e.g. for CHPs (https://www.sciencedirect.com/science/article/pii/S0306261912006551)
- Maximum starts per year, e.g. for CHP, absorbtion chiller
- Ramp rates for large devcies (maximum load increase from one time steps to the next)

## Gurobi solver tuning
There are numerous possibilities to reduce the computation time of solcing the (MI)LP model. One very important way is to imporove numerics of the model by eliminate very large coefficients in the LP-matrix. This can be done by adjusting units (e.g. Watt to Kilo Watt). Another possibility is to use the Gurobi parameter tuning tool. This function trys to find a parameter configuration of the sovler that solves the model more efficiently. Example code for calling this function is    

```python
import sys
from gurobipy import *

# Read the model
model = read("D:\\data\\models\\model.lp")

# Set the TuneResults parameter to 1
model.Params.tuneResults = 1
model.params.tuneTrials = 1
model.params.tuneTimeLimit = 1500
# Tune the model
model.tune()

if model.tuneResultCount > 0:

    # Load the best tuned parameters into the model
    model.getTuneResult(0)

    # Write tuned parameters to a file
    model.write("D:\\data\\tune.prm")

    # Solve the model using the tuned parameters
    model.optimize()
```

### Contact
For reporting bugs or feedback, please contact Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen Unviersity, Germany [(contact)](http://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team6/~poet/Wirtz-Marco/?allou=1&lidx=1)

