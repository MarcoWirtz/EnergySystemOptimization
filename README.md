# Models and tools for Energy System Optimization
This repo is a collection of (MILP) models and other tools for mathematical optimization methods in the field of energy supply systems.

### Content

- [Models](./README.md#models)
- [Useful tools](./README.md#useful-tools)
- [Documentation](./README.md#documentation)

## Models

Some Python code:


### Basic model
In the folder `Basic_Model` is a basic optimization model written in Python/Gurobi along with its pre-processing and post-processing routines. You can download it and run the file `run_multi_objective.py`.

<img src="https://github.com/MarcoWirtz/EnergySystemOptimization/blob/master/images/level_of_detail.png" width="400">
Other features: max starts per year (CHP, AC, ...), discrete sizing, ((Ramp rates)), on/off-switch or free modulation

### Type day clustering (reasonable option)
In energy system simulations and optimizations approaches often a full year is considered. In many models an hourly time resolution is chosen, which results in 8760 time steps for which steady state conditions are assumed. However, many MILPs are complex and comprise many continuous and binary decision variables for each time step. Therefore, a consideration all 8760 time steps leads to huge computation times. In order to reduce the computational complexity, often so-called *type days* are introduced. All 365 days of a year are reduced to a small number of typical days which represent the entire year. Detailed studies, like [Schütz et al., 2016](https://pdfs.semanticscholar.org/aae0/60d220ca9490c8123abaade3d97ff674c266.pdf) and [Schütz et al., 2018](https://www.sciencedirect.com/science/article/pii/S0960148118306591) investigate the effect of introducing type days in the optimization model.

A basic model utilizing type days is presented in the folder `Basic_Model_type_days`. Here a k-medioids clustering approach is used to cluster 365 days to a specified number of type days. The clustering is done regarding specifiec time serieses. If now renewable energies are considered, the clusteirng of energy demands, such as heating, cooling and electricity demands, is sufficient. If renwable energies play an important role within the energy system, weather data has to be considered in the clustering process as well.

The clustering process is done during the pre-processing in Python. The model is then build up with the clustered demand (and weather data) time serieses in the Gurobi interface. The clustering process represents a seperate optimization problem, which consists of a large number of binary variables. Therefore, full convergence cannot be realized. However, the problem converges fast and small gaps are reached within a few seconds.

The uploaded model in the folder `Basic_Model_type_days` was used to conduct a small parameter study, how the computation time and the optimal energy system changes by varying the number of type days. In [Schütz et al., 2018](https://www.sciencedirect.com/science/article/pii/S0960148118306591) a number of XX type days is considered a good trade-off between computation time and accuracy. However, the number strongly depends on the underlying MILP. The parameter study was conducted for a single-objective optimization (total annualized costs).

| # Type days | Objective function (TAC) | Boiler capacity (MW) | CHP capacity (MW) | Compression chiller capacity (MW) | Absorption chiller capacity (MW) |
| -- |:-- | -- |-- | --:| --:|
| # | TAC | Boiler | CHP | CC | AC |
| # | TAC | Boiler | CHP | CC | AC |
| # | TAC | Boiler | CHP | CC | AC |


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


### Objective functions
#### Total annualized costs
```python
model.addConstr(obj["tac"] == sum(c_inv[dev] for dev in all_devs) + sum(c_om[dev] for dev in all_devs)  
                                  + gas_total * param["price_gas"] + from_grid_total * param["price_el"] - to_grid_total * param["revenue_feed_in"], "sum_up_TAC")
    
```

#### CO2 emissions (onsite)
CO2 emissions that result from burning fossil fuels by the devices itself (e.g. boiler, chp, ...)
```python
model.addConstr(obj["co2_onsite"] == gas_total * param["gas_CO2_emission"], "sum_up_onsite_CO2_emissions")
```
with
```python
gas_total = sum(sum(tau[t] * gas[device][t] for t in time_steps) for device in ["BOI", "CHP"])
```  

#### CO2 emissions (gross)
CO2 emissions that result from 
a) burning fossil fuels by the devices itself (e.g. boiler, chp, ...),
b) power supply from national grid
```python
model.addConstr(obj["co2_gross"] == gas_total * param["gas_CO2_emission"] + from_grid_total * param["grid_CO2_emission"], "sum_up_gross_CO2_emissions")
```

#### CO2 emissions (net)
CO2 emissions that result from 
- burning fossil fuels by the devices itself (e.g. boiler, chp, ...),
- power supply from national grid
- avoided burden through power feed-in (negative emissions) 
```python
model.addConstr(obj["co2_net"] == gas_total * param["gas_CO2_emission"] + (from_grid_total - to_grid_total) * param["grid_CO2_emission"], "sum_up_net_CO2_emissions")
```    

#### Annualized investment
```python
model.addConstr(obj["ann_invest"] == sum(c_inv[dev] for dev in all_devs))
```

#### Power from grid
```python
model.addConstr(obj["power_from_grid"] == sum(power["from_grid"][t] for t in time_steps))
```

#### Net power from grid
```python
model.addConstr(obj["net_power_from_grid"] == from_grid_total - to_grid_total)
```
with 
```python
from_grid_total = sum(power["from_grid"][t] for t in time_steps)
to_grid_total = sum(power["to_grid"][t] for t in time_steps)
```

#### Renewable generation
Absolute produced energy by renewable energies. (*Remark: Heat should be counted different than electricity.*)
```python
model.addConstr(obj["renewables_abs"] == sum(power["WT"][t] + power["PV"][t] + heat["STC"][t] for t in time_steps))
``` 

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

