# -*- coding: utf-8 -*-
"""

Author: Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen University, Germany

Created: 01.09.2018

"""

from __future__ import division
import gurobipy as gp
import os
import parameter
import json
import time

def run_optim(obj_fn, obj_eps, eps_constr, dir_results):
    assert (obj_eps == "" and eps_constr == "") or (obj_eps != "" and eps_constr != ""), "If there is a bounded objective function, an epsilon constraint should be given."
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Load model parameter
    start_time = time.time()
    
    (devs, param, dem) = parameter.load_params()
    
    time_steps = range(8760)

    # Create set for devices
    all_devs = ["BOI", "CHP", "AC", "CC", "TES"]       
         
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Setting up the model
    
    # Create a new model
    model = gp.Model("Basic_Model")
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Create new variables

    # Purchase decision binary variables (1 if device is installed, 0 otherwise)
    x = {}
    for device in all_devs:
        x[device] = model.addVar(vtype="B", name="x_" + str(device))
            
    # Device's capacity (i.e. nominal power)
    cap = {}
    for device in ["BOI", "CHP", "AC", "CC", "TES"]:
        cap[device] = model.addVar(vtype="C", name="nominal_capacity_" + str(device))
    
    # Gas flow to/from devices
    gas = {}
    for device in ["BOI", "CHP"]:
        gas[device] = {}
        for t in time_steps:
            gas[device][t] = model.addVar(vtype="C", name="gas_" + device + "_t" + str(t))
        
    # Eletrical power to/from devices
    power = {}
    for device in ["CHP", "CC", "from_grid", "to_grid"]:
        power[device] = {}
        for t in time_steps:
            power[device][t] = model.addVar(vtype="C", name="power_" + device + "_t" + str(t))
       
    # Heat to/from devices
    heat = {}
    for device in ["BOI", "CHP", "AC"]:
        heat[device] = {}
        for t in time_steps:
            heat[device][t] = model.addVar(vtype="C", name="heat_" + device + "_t" + str(t))
    
    # Cooling power to/from devices
    cool = {}
    for device in ["CC", "AC"]:
        cool[device] = {}
        for t in time_steps:
            cool[device][t] = model.addVar(vtype="C", name="cool_" + device + "_t" + str(t))
    
    # Storage decision variables
    ch = {}  # Energy flow to charge storage device
    dch = {} # Energy flow to discharge storage device
    soc = {} # State of charge
    
    for device in ["TES"]:
        ch[device] = {}
        dch[device] = {}
        soc[device] = {}
        for t in time_steps:
            ch[device][t] = model.addVar(vtype="C", name="ch_" + device + "_t" + str(t))
            dch[device][t] = model.addVar(vtype="C", name="dch_" + device + "_t" + str(t))
            soc[device][t] = model.addVar(vtype="C", name="soc_" + device + "_t" + str(t))
        soc[device][len(time_steps)] = model.addVar(vtype="C", name="soc_" + device + "_t" + str(len(time_steps)))
        
    # Objective functions
    obj = {}
    set_obj = ["tac", "co2_gross", "power_from_grid", "net_power_from_grid"]
    for k in set_obj:
        obj[k] = model.addVar(vtype="C", lb=-gp.GRB.INFINITY, name="obj_" + k)    
      
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Define objective function

    model.update()
    model.setObjective(obj[obj_fn], gp.GRB.MINIMIZE)
    if obj_eps == "":
        print("-----------\nSingle-objective optimization with objective function: " + obj_fn)
    else:
        if eps_constr >= 0:
            model.addConstr(obj[obj_eps] <= eps_constr * (1 + param["MIPGap"]))
        elif eps_constr < 0:
            model.addConstr(obj[obj_eps] <= eps_constr * (1 - param["MIPGap"]))
        print("-----------\nRun optimization for '" + obj_fn + "'. Epsilon constraint for '" + obj_eps + "': " + str(eps_constr) + ".")


    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Add constraints
    
    #%% CONTINUOUS SIZING OF DEVICES: minimum capacity <= capacity <= maximum capacity
    for device in ["TES"]:
        model.addConstr(cap[device] <= x[device] * devs[device]["max_cap"])
        model.addConstr(cap[device] >= x[device] * devs[device]["min_cap"])
    
    for t in time_steps:
        for device in ["BOI"]:
            model.addConstr(heat[device][t] <= cap[device])
            
        for device in ["CHP"]:
            model.addConstr(power[device][t] <= cap[device])
        
        for device in ["CC", "AC"]:
            model.addConstr(cool[device][t] <= cap[device])

    #%% INPUT / OUTPUT CONSTRAINTS
    for t in time_steps:
        # Boiler
        gas["BOI"][t] = heat["BOI"][t] / devs["BOI"]["eta_th"]
        
        # Combined heat and power
        model.addConstr(power["CHP"][t] == heat["CHP"][t] / devs["CHP"]["eta_th"] * devs["CHP"]["eta_el"])
        model.addConstr(gas["CHP"][t] == heat["CHP"][t] / devs["CHP"]["eta_th"])
        
        # Compression chiller
        model.addConstr(cool["CC"][t] == power["CC"][t] * devs["CC"]["COP"])  

        # Absorption chiller
        model.addConstr(cool["AC"][t] == heat["AC"][t] * devs["AC"]["eta_th"])

    #%% ENERGY BALANCES
    for t in time_steps:
        # Heat balance
        model.addConstr(heat["BOI"][t] + heat["CHP"][t] + dch["TES"][t] == dem["heat"][t] + heat["AC"][t] + ch["TES"][t])

    for t in time_steps:
        # Electricity balance
        model.addConstr(power["CHP"][t] + power["from_grid"][t] == dem["power"][t] + power["to_grid"][t] + power["CC"][t])

    for t in time_steps:
        # Cooling balance
        model.addConstr(cool["AC"][t] + cool["CC"][t] == dem["cool"][t])    
    
    #%% STORAGE DEVICES
    for device in ["TES"]:  
        # Cyclic condition
        model.addConstr(soc[device][len(time_steps)] == soc[device][0])

        for t in range(len(time_steps)+1):
            if t == 0:
                # Set initial state of charge
                model.addConstr(soc[device][0] <= cap[device] * devs[device]["soc_init"])
            else:
                # Energy balance: soc(t) = soc(t-1) + charge - discharge
                model.addConstr(soc[device][t] == soc[device][t-1] * (1-devs[device]["sto_loss"])
                    + (ch[device][t-1] * devs[device]["eta_ch"] 
                    - dch[device][t-1] / devs[device]["eta_dch"]))
                
                # soc_min <= state of charge <= soc_max
                model.addConstr(soc[device][t] <= devs[device]["soc_max"] * cap[device])
                model.addConstr(soc[device][t] >= devs[device]["soc_min"] * cap[device])
                
                # charging power <= maximum charging power and discharging power <= maximum discharging power 
                model.addConstr(ch[device][t-1] <= devs[device]["max_ch"])
                model.addConstr(dch[device][t-1] <= devs[device]["max_dch"])

    #%% SUM UP RESULTS
    gas_total = sum(sum(gas[device][t] for t in time_steps) for device in ["BOI", "CHP"])
  
    from_grid_total = sum(power["from_grid"][t] for t in time_steps)
    to_grid_total = sum(power["to_grid"][t] for t in time_steps)

    # Investments
    c_inv = {}
    for device in all_devs:
        c_inv[device] = cap[device] * devs[device]["ann_inv_var"]

    # Operation and maintenance costs
    c_om = {}
    for device in all_devs: 
        c_om[device] = devs[device]["cost_om"] * (cap[device] * devs[device]["inv_var"])

    #%% OBJECTIVE FUNCTIONS
    # TOTAL ANNUALIZED COSTS
    model.addConstr(obj["tac"] == sum(c_inv[dev] for dev in all_devs) + sum(c_om[dev] for dev in all_devs)  
                                  + gas_total * param["price_gas"] + from_grid_total * param["price_el"] - to_grid_total * param["revenue_feed_in"], "sum_up_TAC")
    
    # ANNUAL CO2 EMISSIONS: Implicit emissions by power supply from national grid is penalized, feed-in is ignored
    model.addConstr(obj["co2_gross"] == gas_total * param["gas_CO2_emission"] + from_grid_total * param["grid_CO2_emission"], "sum_up_gross_CO2_emissions")
    
    # POWER PROVIDED BY GRID
    model.addConstr(obj["power_from_grid"] == from_grid_total)
    
    # NET POWER PROVIDED BY GRID
    model.addConstr(obj["net_power_from_grid"] == from_grid_total - to_grid_total)
    
    
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Set model parameters and execute calculation
    
    print("Precalculation and model set up done in %f seconds." %(time.time() - start_time))
    
    # Set solver parameters
    model.Params.MIPGap     = param["MIPGap"]   # ---,         gap for branch-and-bound algorithm
    model.Params.method     = 2                 # ---,         -1: default, 0: primal simplex, 1: dual simplex, 2: barrier, etc.
    model.Params.Heuristics = 0
    model.Params.MIPFocus   = 2
    model.Params.Cuts       = 3
    model.Params.PrePasses  = 8
    
    # Execute calculation
    start_time = time.time()

    model.optimize()

    print("Optimization done. (%f seconds.)" %(time.time() - start_time))
    
   
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Check and save results
    
    if not os.path.exists(dir_results):
        os.makedirs(dir_results)
    
    # Check if optimal solution was found
    if model.Status in (3,4) or model.SolCount == 0:  # "INFEASIBLE" or "INF_OR_UNBD"
        model.computeIIS()
        model.write(dir_results + "\\" + "model.ilp")
        print('Optimization result: No feasible solution found.')
    
    else:
        # Save results
        save_results(devs, param, dem, model, obj_fn, obj_eps, eps_constr, dir_results)
        
        # Return dictionary
        res_obj = {}        
        for k in set_obj:
            res_obj[k] = obj[k].x
        return res_obj
    
def save_results(devs, param, dem, model, obj_fn, obj_eps, eps_constr, dir_results):
    
    # Write model parameter in json-file
    all_param = {**param, **devs}
    with open(dir_results + "\parameter.json", "w") as outfile:
        json.dump(all_param, outfile, indent=4, sort_keys=True)

    # Write Gurobi files
    model.write(dir_results + "\model.lp")
    model.write(dir_results + "\model.prm")
    model.write(dir_results + "\model.sol")
    
    # Save demands
    with open(dir_results + "\demands.txt", "w") as outfile:
        for com in dem.keys():
            for t in range(8760):
                outfile.write(com + "_t" + str(t) + " " + str(dem[com][t]) + "\n")
                
    # Write further information in txt-file
    with open(dir_results + "\meta_results.txt", "w") as outfile:
        outfile.write("Runtime " + str(round(model.Runtime,6)) + "\n")
        outfile.write("ObjectiveValue " + "{0}".format(model.ObjVal) + "\n")
        outfile.write("ModelStatus " + "{0}".format(model.Status) + "\n")
        outfile.write("NodeCount " + "{0}".format(model.NodeCount) + "\n")
        outfile.write("MIPGap " + "{0}".format(model.Params.MIPGap) + "\n\n")
        outfile.write("ObjectiveFunction " + obj_fn + "\n")
        outfile.write("BoundedFunction " + obj_eps + "\n")
        outfile.write("EpsilonConstraint " + str(eps_constr) + "\n\n")
                    
    print("\nResult files (parameter.json, results.txt, demands.txt, model.lp, model.rpm, model.sol) saved in " + dir_results)