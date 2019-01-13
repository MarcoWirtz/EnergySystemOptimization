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

The visualization methods "post_processing.py" presented below use these output files to create illustrative plots to visualize and analyse the numeric results. Among others one plot shows the Yearly plot (averaged over months) (1 plot)
#### Monthly plot (averaged over days) (12 plots)
#### Daily plot (365 plots)
#### Carpet plot
#### Box plot (daily profile)
#### Box plot (seasonal profile)
#### Scatter density plot

#### Matrix illustration


- ... models are tested with Pyhton X.X, Gurobi version X.X.

## Modeling approaches 
<img src="https://github.com/MarcoWirtz/EnergySystemOptimization/blob/master/images/level_of_detail.png" width="400">
Other features: max starts per year (CHP, AC, ...), discrete sizing, ((Ramp rates)), on/off-switch or free modulation; coraser time reolution (2 h, 4 h), costs for start up of CHP (https://www.sciencedirect.com/science/article/pii/S0306261912006551)

### Type day clustering (reasonable option)
In energy system simulations and optimizations approaches often a full year is considered. In many models an hourly time resolution is chosen, which results in 8760 time steps for which steady state conditions are assumed. However, many MILPs are complex and comprise many continuous and binary decision variables for each time step. Therefore, a consideration all 8760 time steps leads to huge computation times. In order to reduce the computational complexity, often so-called *type days* are introduced. All 365 days of a year are reduced to a small number of typical days which represent the entire year. Detailed studies, like [Schütz et al., 2016](https://pdfs.semanticscholar.org/aae0/60d220ca9490c8123abaade3d97ff674c266.pdf) and [Schütz et al., 2018](https://www.sciencedirect.com/science/article/pii/S0960148118306591) investigate the effect of introducing type days in the optimization model.

A basic model utilizing type days is presented in the folder `Basic_Model_type_days`. Here a k-medioids clustering approach is used to cluster 365 days to a specified number of type days. The clustering is done regarding specifiec time serieses. If now renewable energies are considered, the clusteirng of energy demands, such as heating, cooling and electricity demands, is sufficient. If renwable energies play an important role within the energy system, weather data has to be considered in the clustering process as well.

The clustering process is done during the pre-processing in Python. The model is then build up with the clustered demand (and weather data) time serieses in the Gurobi interface. The clustering process represents a seperate optimization problem, which consists of a large number of binary variables. Therefore, full convergence cannot be realized. However, the problem converges fast and small gaps are reached within a few seconds.

In [Schütz et al., 2018](https://www.sciencedirect.com/science/article/pii/S0960148118306591) a number of XX type days is considered a good trade-off between computation time and accuracy. However, the number strongly depends on the underlying MILP. The parameter study was conducted for a single-objective optimization (total annualized costs).

### Piece-wise linear investment (reasonable option)
no many binary variables are required
important influence on he optimiation results
TES als Beispiel, 

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
BOI als Beispiel, AbbildungsDoku mit Diagramm, Kurzergebnisse (Vergleich zu konstantem eta)


## Gurobi solver tuning
There are numerous possibilities to reduce the computation time of solcing the (MI)LP model. One very important way is to imporove numerics of the model by eliminate very large coefficients in the LP-matrix. This can be done by adjusting units (e.g. Watt to Kilo Watt). Another possibility is to use the Gurobi parameter tuning tool. This function trys to find a parameter configuration of the sovler that solves the model more efficiently. Example code for calling this function is    

```
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

