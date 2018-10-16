# -*- coding: utf-8 -*-

"""

Author: Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen University, Germany

Created: 01.09.2018

"""


import numpy as np
import json
import post_processing_plot
import os
import time


def read_solution_file(file_name, time_series_list, time_steps):
    start_time = time.time()
    
    # Read file
    with open(file_name, "r") as solution_file:
        file = solution_file.readlines()
    
    # Initialize time series as numpy arrays
    time_series_flows = {}
    for flow in time_series_list:
        # If storage, one time step more
        if "soc" in flow:
            time_series_flows[flow] = np.zeros(time_steps+1)
        else:
            time_series_flows[flow] = np.zeros(time_steps)
            
    # Initialize dictionary for all other variables
    other_dec_var = {}
    cap = {}

    # Parse all lines of the solution file
    for line in range(len(file)):
        line_found = 0
        line_list = file[line].split(" ")
        split_t = line_list[0].split("_t")
        for flow in time_series_list:
            if flow == "_t".join(split_t[0:-1]):
                time_step = split_t[-1]
                time_series_flows[flow][int(time_step)] = float(line_list[1])
                line_found = 1
                break
        if line_found == 0:
            # Lines with "#" at the beginning are ignored
            if file[line][0] != "#": 
                other_dec_var[line_list[0]] = line_list[1]
                if "nominal_capacity_" in line_list[0]:
                    cap[line_list[0][17:]] = float(line_list[1])
                line_found = 1
    
    print("Reading solution took %f seconds." %(time.time() - start_time))
    return time_series_flows, other_dec_var, cap
    
def read_demand_file(file_name, demand_list, time_steps):
    start_time = time.time()
    
    # Read file
    with open(file_name, "r") as demand_file:
        file = demand_file.readlines()
    
    # Initialize time series as numpy arrays
    time_series_dem = {}
    for dem in demand_list:
        time_series_dem[dem + "_dem"] = np.zeros(time_steps)

    # Parse all lines of the solution file
    for line in range(len(file)):
        line_list = file[line].split(" ")
        split_t = line_list[0].split("_t")
        for dem in demand_list:
            if dem == "_t".join(split_t[0:-1]):
                time_step = split_t[-1]
                var_val = float(line_list[1])
                time_series_dem[dem + "_dem"][int(time_step)] = var_val
                break
    
    print("Reading demands took %f seconds." %(time.time() - start_time))
    return time_series_dem


def run_post_processing(dir_results):
    
    tech_list = ["heat_BOI", "heat_CHP", "power_CHP", 
#                 "heat_EH", "power_EH",
#                 "heat_ASHP", "power_ASHP", 
                 "power_from_grid", "power_to_grid",
#                 "power_WT", "power_PV", "heat_STC", 
                 "cool_AC", "heat_AC", "cool_CC", "power_CC", 
                 "ch_TES", "dch_TES", "soc_TES", #"ch_CTES", "dch_CTES", "soc_CTES", "ch_BAT", "dch_BAT", "soc_BAT", 
                 ]
    
    demand_list = ["heat", "cool", "power"]
    
    number_steps = 8760
    
    #%% Load data and create plots   
    folder_list = os.listdir(dir_results)
    for folder in folder_list:
        if "pareto" in folder:
            print("------------\nPost-processing: " + folder)
            time_series_flows, other_dec_var, cap = read_solution_file(dir_results + "\\" + folder + "\\model.sol", tech_list, number_steps)
            time_series_dem = read_demand_file(dir_results + "\\" + folder + "\demands.txt", demand_list, number_steps)
            time_series = {**time_series_flows, **time_series_dem}
            params = json.loads(open(dir_results + "\\" + folder + "\parameter.json" ).read())
            
            # Create plots
            print("Create plots...")
            start_time = time.time()
            post_processing_plot.plot_time_series(time_series, {"yearly": 1, "monthly": 0, "daily": 0}, dir_results)
            print("All plots created (%f seconds)." %(time.time() - start_time))
            
        elif "anchor" in folder:
            print("------------\nPost-processing: " + folder)
            time_series_flows, other_dec_var, cap = read_solution_file(dir_results + "\\" + folder + "\\model.sol", tech_list, number_steps)
            time_series_dem = read_demand_file(dir_results + "\\" + folder + "\demands.txt", demand_list, number_steps)
            time_series = {**time_series_flows, **time_series_dem}
            params = json.loads(open(dir_results + "\\" + folder + "\parameter.json" ).read())
            
            # Create plots
            print("Create plots...")
            start_time = time.time()
#            post_processing_plot.plot_time_series(time_series, {"yearly": 1, "monthly": 1, "daily": 0}, dir_results + "\\" + folder)
#            post_processing_plot.plot_device(time_series, dir_results + "\\" + folder)
            post_processing_plot.plot_capacity(cap, time_series, dir_results + "\\" + folder)
#            post_processing_plot.save_energy_flows(time_series, params, dir_results + "\\" + folder)
            print("All plots created (%f seconds)." %(time.time() - start_time))
            
        else:
            continue
    
    # TODO:    
    # Create pareto plots
    # Create "run_single_objective.py"
    # Implement curtailed energy in time series plots: time_series["max_heat_STC"] = params["STC"]["heat"]
            

#%%
if __name__ == "__main__":
    
    # Set result directory that should be evaluated:
    dir_results = "D:\\mwi\\Gurobi_Modelle\\EnergySystemOptimization\\Basic_Model\\Results\\2018-10-11_15-05-43_multi-objective__tac__co2_gross"
        
    run_post_processing(dir_results)