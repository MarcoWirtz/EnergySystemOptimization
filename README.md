# Models and tools for Energy System Optimization
This repo is a collection of (MILP) models and other tools for mathematical optimization methods in the field of energy systems.

### Content

- [Models](./README.md#models)
- [Useful tools](./README.md#useful-tools)
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

### Objective functions
#### Total annualized costs
```
model.addConstr(obj["tac"] == sum(c_inv[dev] for dev in all_devs) + sum(c_om[dev] for dev in all_devs)  
                                  + gas_total * param["price_gas"] + from_grid_total * param["price_el"] - to_grid_total * param["revenue_feed_in"], "sum_up_TAC")
    
```

#### CO2 emissions (onsite)
CO2 emissions that result from burning fossil fuels by the devices itself (e.g. boiler, chp, ...)
```
model.addConstr(obj["co2_onsite"] == gas_total * param["gas_CO2_emission"], "sum_up_onsite_CO2_emissions")
```
with
```
gas_total = sum(sum(tau[t] * gas[device][t] for t in time_steps) for device in ["BOI", "CHP"])
```  

#### CO2 emissions (gross)
CO2 emissions that result from 
a) burning fossil fuels by the devices itself (e.g. boiler, chp, ...),
b) power supply from national grid
```
model.addConstr(obj["co2_gross"] == gas_total * param["gas_CO2_emission"] + from_grid_total * param["grid_CO2_emission"], "sum_up_gross_CO2_emissions")
```

#### CO2 emissions (net)
CO2 emissions that result from 
- burning fossil fuels by the devices itself (e.g. boiler, chp, ...),
- power supply from national grid
- avoided burden through power feed-in (negative emissions) 
```
model.addConstr(obj["co2_net"] == gas_total * param["gas_CO2_emission"] + (from_grid_total - to_grid_total) * param["grid_CO2_emission"], "sum_up_net_CO2_emissions")
```    

#### Annualized investment
```
model.addConstr(obj["ann_invest"] == sum(c_inv[dev] for dev in all_devs))
```

#### Power from grid
```
model.addConstr(obj["power_from_grid"] == sum(power["from_grid"][t] for t in time_steps))
```

#### Net power from grid
```
model.addConstr(obj["net_power_from_grid"] == from_grid_total - to_grid_total)
```
with 
```
from_grid_total = sum(power["from_grid"][t] for t in time_steps)
to_grid_total = sum(power["to_grid"][t] for t in time_steps)
```

#### Renewable generation
Absolute produced energy by renewable energies. (*Remark: Heat should be counted different than electricity.*)
```
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

