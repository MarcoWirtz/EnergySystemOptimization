# -*- coding: utf-8 -*-
"""

Author: Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen University, Germany

Created: 01.09.2018

"""

import matplotlib.pyplot as plt
import numpy as np
import datetime
import os

#%%
def save_energy_flows(time_series, params, dir_results):
     
    time_steps = range(8760)
    
    sum_distr = {}
    heat_sources = ["heat_BOI", "heat_CHP", "heat_EH", "heat_ASHP", "heat_STC", "dch_TES"]
    cool_sources = ["cool_CC", "cool_AC", "dch_CTES"]
    elec_sources = ["power_WT", "power_CHP", "power_from_grid", "power_PV", "dch_BAT"]
    tech_color = get_tech_color()
    
    consum = {}
    
    # Heating
    consum["heat"] = {}
    for t in time_steps:
        # Sum heat consumption for every time step as fraction
        heat_sinks = ["heat_dem", "ch_TES", "heat_AC"]
        consum["heat"][t] = np.array([time_series[k][t] for k in heat_sinks])
        if sum(consum["heat"][t]) == 0:
            consum["heat"][t] = np.zeros(len(heat_sinks))
        else:
            consum["heat"][t] = consum["heat"][t] / sum(consum["heat"][t])
    
    for dev in heat_sources:
        sum_distr[dev] = np.zeros(len(heat_sinks))
        for t in time_steps:
            # only boiler: ch, demand, ac
            sum_distr[dev] = sum_distr[dev] + time_series[dev][t] * consum["heat"][t]
 
    # Cooling
    consum["cool"] = {}
    for t in time_steps:
        # Sum cooling consumption for every time step as fraction
        cool_sinks = ["cool_dem", "ch_CTES"]
        consum["cool"][t] = np.array([time_series[k][t] for k in cool_sinks])
        if sum(consum["cool"][t]) == 0:
            consum["cool"][t] = np.zeros(len(cool_sinks))
        else:
            consum["cool"][t] = consum["cool"][t] / sum(consum["cool"][t])
    
    for dev in cool_sources:
        sum_distr[dev] = np.zeros(len(cool_sinks))
        for t in time_steps:
            sum_distr[dev] = sum_distr[dev] + time_series[dev][t] * consum["cool"][t]
            
    # Electricity
    consum["elec"] = {}
    for t in time_steps:
        # Sum electricity consumption for every time step as fraction
        time_series["power_dem"]
        elec_sinks = ["power_dem", "power_to_grid", "power_EH", "power_ASHP", "power_CC", "ch_BAT"]
        consum["elec"][t] = np.array([time_series[k][t] for k in elec_sinks])
        if sum(consum["elec"][t]) == 0:
            consum["elec"][t] = np.zeros(len(elec_sinks))
        else:
            consum["elec"][t] = consum["elec"][t] / sum(consum["elec"][t])
    
    for dev in elec_sources:
        sum_distr[dev] = np.zeros(len(elec_sinks))
        for t in time_steps:
            sum_distr[dev] = sum_distr[dev] + time_series[dev][t] * consum["elec"][t]  
    
    # Create plots: heat
    sources_color = [tech_color[dev] for dev in heat_sources]    
    for k in range(len(consum["heat"][0])):
        fig1, ax1 = plt.subplots(figsize=(10,5))
        plt.rcParams.update({'font.size': 14})
        heat_dem_sources = [float(sum_distr[dev][k]) for dev in heat_sources]
        patches, texts, hj = plt.pie(heat_dem_sources, colors=sources_color, autopct="%1.1f%%", pctdistance=1.2)
        plt.legend(patches, heat_sources, bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        ax1.axis('equal')
        file_name = dir_results + "//Supply_" + heat_sinks[k]
        plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
#        plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
#        print("Created plot '" + file_name + "' successfully.")
        plt.clf()
        plt.close()
    
    # Create plots: cooling
    sources_color = [tech_color[dev] for dev in cool_sources]    
    for k in range(len(consum["cool"][0])):
        fig1, ax1 = plt.subplots(figsize=(10,5))
        plt.rcParams.update({'font.size': 14})
        cool_dem_sources = [float(sum_distr[dev][k]) for dev in cool_sources]
        patches, texts, hj = plt.pie(cool_dem_sources, colors=sources_color, autopct="%1.1f%%", pctdistance=1.2)
        plt.legend(patches, cool_sources, bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        ax1.axis('equal')
        file_name = dir_results + "//Supply_" + cool_sinks[k]
        plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
#        plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
#        print("Created plot '" + file_name + "' successfully.")
        plt.clf()
        plt.close()
        
    # Create plots: electricity
    sources_color = [tech_color[dev] for dev in elec_sources]    
    for k in range(len(consum["elec"][0])):
        fig1, ax1 = plt.subplots(figsize=(10,5))
        plt.rcParams.update({'font.size': 14})
        elec_dem_sources = [float(sum_distr[dev][k]) for dev in elec_sources]
        patches, texts, hj = plt.pie(elec_dem_sources, colors=sources_color, autopct="%1.1f%%", pctdistance=1.2)
        plt.legend(patches, elec_sources, bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        ax1.axis('equal')
        file_name = dir_results  + "//Supply_" + elec_sinks[k]
        plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
#        plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
#        print("Created plot '" + file_name + "' successfully.")
        
        plt.clf()
        plt.close()
        
    #%% Write csv-file
    fout = dir_results + "//Energy_flow.csv"
    fo = open(fout, "w")
    fo.write("Heat suppliers, heat_dem, TES_ch, AC_h\n")
    for dev in heat_sources:
        helpList = [sum_distr[dev][k] for k in range(len(sum_distr[dev]))]
        helpList_split = str(helpList).strip('[]')
        fo.write(dev + "," + str(helpList_split) + "\n")
        
    fo.write("\nCooling suppliers, cool_dem, CTES_ch\n")
    for dev in cool_sources:
        helpList = [sum_distr[dev][k] for k in range(len(sum_distr[dev]))]
        helpList_split = str(helpList).strip('[]')
        fo.write(dev + "," + str(helpList_split) + "\n")
        
    fo.write("\nElectricity suppliers, power_dem, power_to_grid, EH_p, ASHP_p, CC_p, BAT_ch\n")
    for dev in elec_sources:
        helpList = [sum_distr[dev][k] for k in range(len(sum_distr[dev]))]
        helpList_split = str(helpList).strip('[]')
        fo.write(dev + "," + str(helpList_split) + "\n")
        
    fo.close()
#    print("Saved energy flow data successfully.")
    
#%% plots comprehensive operation information for devices
def plot_device(time_series, dir_results):
    
    month_begins = {0: 1, 1: 31, 2: 59, 3: 90, 4: 120, 5: 151, 6:181, 7: 212, 8:243, 9:273, 10:304, 11:334, 12:365}
    month_mids = {0: 15.5, 1: 45, 2: 74.5, 3: 105, 4: 135.5, 5: 166, 6: 196.5, 7: 227.5, 8: 258, 9: 288.5, 10: 319, 11: 349.5}
    month_tuple = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
    
    device_name = {"heat_BOI": "Boiler", 
                   "power_CHP": "CHP (internal combustion engine)",
                   "heat_EH": "Electric heater",
                   "heat_ASHP": "Heat pump (air/water)",
                   "cool_CC": "Compression chiller", "cool_AC": "Absorption chiller",
                   "power_PV": "Photovoltaic (roof-top)", 
                   "power_WT": "Wind turbine", "heat_STC": "Solar thermal collector", "heat_dem": "Heating demand", "cool_dem": "Cooling demand",
                   "power_dem": "Power demand", "power_from_grid": "Electric power from grid", "power_to_grid": "Electric power to grid",
                   "soc_TES": "Heat thermal energy storage", "soc_CTES": "Cold thermal energy storage", "BAT": "Battery"}


    for device in ["heat_BOI", "power_CHP", "soc_TES"]:
    
        if device in ["heat_BOI", "heat_EH", "heat_ASHP", "heat_STC", "heat_dem", "ch_TES", "dch_TES"]:
            cmap_color = "Reds"
            box_color = "lightsalmon"
            y_label = "Heat output in MW"
            
        elif device in ["cool_CC", "cool_AC", "cool_dem", "ch_CTES", "dch_CTES"]:
            cmap_color = "Blues"
            box_color = "lightblue"    
            y_label = "Cooling output in MW"
            
        elif device in ["power_WT", "power_PV", "power_dem", "power_from_grid", "power_to_grid"]:
            cmap_color = "Greys"
            box_color = "lightgray"   
            y_label = "Electrical power in MW"
            
        elif device in ["soc_TES"]:
            cmap_color = "Reds"
            box_color = "lightsalmon"
            y_label = "State of charge in MWh"
            
        elif device in ["soc_CTES"]:
            cmap_color = "Blues"
            box_color = "lightblue"    
            y_label = "State of charge in MWh"
            
        elif device in ["soc_BAT"]:
            cmap_color = "Greys"
            box_color = "lightgray" 
            y_label = "State of charge in MWh"
            
        # Rewrite time series dict in two-dimensional dict
        data = np.zeros([24,365])
        for t in range(8760):
            data[23-(t % 24), t // 24] = time_series[device][t]
        
        fig = plt.figure(figsize=(10,10))
        plt.rc('font', size=15)
        
        # First plot: Yearly profile
        ax = fig.add_subplot(311)
        im = ax.imshow(data, interpolation='none', extent=[0,365,0,24], aspect=4, cmap=cmap_color)
        cbar = fig.colorbar(im, orientation="horizontal", shrink=0.7, pad=0.2, aspect=40)
        cbar.set_label(y_label)
        plt.yticks([0, 6, 12, 18, 24])
        plt.xticks([month_mids[k] for k in range(12)], month_tuple)
        plt.title(device_name[device])
        
        # Second plot: Daily profile
        fig.add_subplot(312, ylabel=y_label, title="Daily profile")
        plt.boxplot(np.transpose(np.flip(data,0)),0,'',whis="range",patch_artist=True,boxprops=dict(facecolor=box_color),medianprops=dict(color="black"))
        
        # Third plot: Monthly profile
        fig.add_subplot(313, ylabel=y_label, title = "Seasonal profile")
        data_month = {}
        for k in range(12):
            data_month[k] = np.concatenate((data[:,month_begins[k]-1:month_begins[k+1]-1]), 0)
        plt.boxplot([data_month[k] for k in range(12)],0,'',whis="range",patch_artist=True,boxprops=dict(facecolor=box_color),medianprops=dict(color="black"))
        plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], month_tuple)
        plt.tight_layout()
        
        # Save plot
        file_name = dir_results + "//Operation_" + device
        plt.savefig(file_name + ".png", dpi = 400, format = "png", bbox_inches="tight", pad_inches=0.1)
    #    plt.savefig(file_name + ".pdf", dpi = 400, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    #    print("Created plot '" + file_name + "' successfully.")
        plt.clf()
        plt.close()

def plot_time_series(time_series, plot_mode, dir_results):

    # Start/end day of each month
    first_day = np.array([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
    last_day = np.array([31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365])
    month_tuple = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")

    H = {} # help dicitionary
    d = {} # contains mean values for 365 days
    D = {} # help dicitionary
    M = {} # contains mean values for 12 months
         
    for device in time_series.keys():
        H[device] = {}
        d[device] = np.zeros(365)
        D[device] = {}
        M[device] = np.zeros(12)
    
    # Divide time series (8760 time steps) into daily (H), monthly (D) and yearly profiles (M)
    for device in time_series.keys():
        for k in range(365):
            H[device][k] = time_series[device][(k*24):(k*24+24)]
            d[device][k] = sum(time_series[device][(k*24):(k*24+24)])/24
    
        for m in range(12):
            D[device][m] = d[device][first_day[m]:last_day[m]]
            M[device][m] = sum(d[device][first_day[m]:last_day[m]])/(last_day[m]-first_day[m])
    
    heat_dict = {}
    cool_dict = {}
    power_dict = {}
    sto_dict = {}   
            
    #%% Plot yearly profile  
    if plot_mode["yearly"] == 1:
        for dev in time_series.keys():
            if "heat" in dev or "ch_TES" in dev or "dch_TES" in dev:
                heat_dict[dev] = M[dev]
            if "cool" in dev or "ch_CTES" in dev or "dch_CTES" in dev:
                cool_dict[dev] = M[dev]
            if "power" in dev or "ch_BAT" in dev or "dch_BAT" in dev:
                power_dict[dev] = M[dev]
                
        for dev in ["soc_TES", "soc_CTES", "soc_BAT"]:
            sto_dict[dev] = M[dev][m]  
    
        save_name = dir_results + "//Year_Profile"
        plot_interval(heat_dict, cool_dict, power_dict, save_name, "Month")
        save_name = dir_results + "//Year_Profile_Storage"
        plot_interval_storage(M, save_name, "Month")
    
    #%% Plot monthly profile
    if plot_mode["monthly"] == 1:  
        for m in range(12):
            for dev in time_series.keys():
                if "heat" in dev or "ch_TES" in dev or "dch_TES" in dev:
                    heat_dict[dev] = D[dev][m]
                if "cool" in dev or "ch_CTES" in dev or "dch_CTES" in dev:
                    cool_dict[dev] = D[dev][m]  
                if "power" in dev or "ch_BAT" in dev or "dch_BAT" in dev:
                    power_dict[dev] = D[dev][m]
            save_name = dir_results + "//" + str(m+1) + "_" + month_tuple[m]
            plot_interval(heat_dict, cool_dict, power_dict, save_name, "Day")
            for dev in ["soc_TES", "soc_CTES", "soc_BAT"]:
                sto_dict[dev] = D[dev][m]
            save_name = dir_results + "//" + str(m+1) + "_" + month_tuple[m] + "_Storage"
            plot_interval_storage(sto_dict, save_name, "Day")
            
    #%% Plot daily profile
    if plot_mode["daily"] == 1:
        for d in range(365): # full year: range(365)
            month_name = (datetime.date(2018,1,1) + datetime.timedelta(days=d)).strftime("%b")
            month_num = (datetime.date(2018,1,1) + datetime.timedelta(days=d)).strftime("%m")
            day_num = (datetime.date(2018,1,1) + datetime.timedelta(days=d)).strftime("%d")
            # Create result folder for month
            if not os.path.exists(dir_results + "//" + str(month_num) + "_" + month_name):
                os.makedirs(dir_results + "//" + str(month_num) + "_" + month_name)
            for dev in time_series.keys():
                if "heat" in dev or "ch_TES" in dev or "dch_TES" in dev:
                    heat_dict[dev] = H[dev][d]
                if "cool" in dev or "ch_CTES" in dev or "dch_CTES" in dev:
                    cool_dict[dev] = H[dev][d]  
                if "power" in dev or "ch_BAT" in dev or "dch_BAT" in dev:
                    power_dict[dev] = H[dev][d]
            save_name = dir_results + "//" + str(month_num) + "_" + month_name + "//" + month_name + "_" + str(day_num)
            plot_interval(heat_dict, cool_dict, power_dict, save_name, "Time [hours]")
            for dev in ["soc_TES", "soc_CTES", "soc_BAT"]:
                sto_dict[dev] = H[dev][d]
            save_name = dir_results + "//" + str(month_num) + "_" + month_name + "//" + month_name + "_" + str(day_num) + "_Storage"
            plot_interval_storage(sto_dict, save_name, "Time [hours]")
    
    #%% plots a time series of abitrary length
def plot_interval(heat, cool, power, save_name, xTitle):
    tech_color = get_tech_color()
    label_dev = {"heat_BOI": "Boiler",
                 "heat_CHP": "ICE (CHP)",
                 "heat_EH": "E-heater",
                 "heat_ASHP": "AS heat pump",
                 "dch_TES": "HTES (discharge)",
                 "heat_STC": "STC",
#                 "STC_curtail": "STC (curtailed)",
                 "cool_CC": "Comp. chiller",
                 "cool_AC": "Abs. chiller",
                 "dch_CTES": "CTES (discharge)",
                 "power_CHP": "ICE (CHP)",
                 "power_WT": "Wind",
                 "power_PV": "PV",
                 "power_from_grid": "Grid power",
                 "dch_BAT": "Battery (discharge)",
#                 "PV_curtail": "PV (curtailed)",
#                 "WT_curtail": "Wind (curtailed)",
                 }

    # Transform data for plots: heating
    heat_res = {}    
    heat_labels = []
    heat_res_list = []
    heat_color = []
    for device in ["heat_BOI", "heat_CHP", "heat_EH", "heat_ASHP", "dch_TES", "heat_STC"]:#, "STC_curtail"]:
        heat_res[device] = np.zeros(2*heat[device].size)
        for t in range(heat[device].size):            
            heat_res[device][2*t:2*t+2] = [heat[device][t], heat[device][t]]
        heat_res_list.extend([heat_res[device].tolist()])
        heat_labels.append(label_dev[device])
        heat_color.extend([tech_color[device]])    
    for device in ["heat_dem", "heat_AC", "ch_TES"]:    
        heat_res[device] = np.zeros(2*heat[device].size)
        for t in range(heat[device].size):
            heat_res[device][2*t:2*t+2] = [heat[device][t], heat[device][t]]
            
    # Transform data for plots: cooling
    cool_res = {}    
    cool_labels = []
    cool_res_list = []
    cool_color = []
    for device in ["cool_CC", "cool_AC", "dch_CTES"]:
        cool_res[device] = np.zeros(2*cool[device].size)
        for t in range(cool[device].size):            
            cool_res[device][2*t:2*t+2] = [cool[device][t], cool[device][t]]
        cool_res_list.extend([cool_res[device].tolist()])
        cool_labels.append(label_dev[device])
        cool_color.extend([tech_color[device]])    
    for device in ["cool_dem", "ch_CTES"]:    
        cool_res[device] = np.zeros(2*cool[device].size)
        for t in range(cool[device].size):
            cool_res[device][2*t:2*t+2] = [cool[device][t], cool[device][t]]

    # Transform data for plots: power
    power_res = {}    
    power_labels = []
    power_res_list = []
    power_color = []
    for device in ["power_CHP", "power_WT", "power_PV", "power_from_grid", "dch_BAT"]:#, "PV_curtail", "WT_curtail"]:
        power_res[device] = np.zeros(2*power[device].size)
        for t in range(power[device].size):            
            power_res[device][2*t:2*t+2] = [power[device][t], power[device][t]]
        power_res_list.extend([power_res[device].tolist()])
        power_labels.append(label_dev[device])
        power_color.extend([tech_color[device]])
    for device in ["power_dem", "power_CC", "power_EH", "power_ASHP", "ch_BAT", "power_to_grid"]:    
        power_res[device] = np.zeros(2*power[device].size)
        for t in range(power[device].size):
            power_res[device][2*t:2*t+2] = [power[device][t], power[device][t]]

    # Create time ticks for x-axis
    timeTicks = [0]
    for t in range(heat["heat_BOI"].size):
        timeTicks.extend([timeTicks[-1] + 1])
        timeTicks.extend([timeTicks[-2] + 1])
    del timeTicks[-1]

    # Create figure
    plt.figure(figsize=(12, 9))
    plt.rcParams.update({'font.size': 14})

    # Create subplot: heat balance
    plt.subplot(311, ylabel = "Heating output in MW", xlabel = " ")
    plt.stackplot(timeTicks, np.vstack(heat_res_list), labels=heat_labels, colors=heat_color)
    plt.plot(timeTicks, heat_res["heat_dem"]+heat_res["heat_AC"]+heat_res["ch_TES"], color=tech_color["ch_TES"], linewidth = 3, label="HTES (charge)")
    plt.plot(timeTicks, heat_res["heat_dem"]+heat_res["heat_AC"], color=tech_color["heat_AC"], linewidth = 3, label="AC demand")
    plt.plot(timeTicks, heat_res["heat_dem"], color="black", linewidth = 3, label="Heating demand")

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)

    # Create second subplot: cooling balance
    plt.subplot(312, ylabel = "Cooling output in MW", xlabel = " ")
    plt.stackplot(timeTicks, np.vstack(cool_res_list), labels=cool_labels, colors=cool_color)
    plt.plot(timeTicks, cool_res["cool_dem"]+cool_res["ch_CTES"], color=tech_color["ch_CTES"], linewidth = 3, label="CTES (charge)")
    plt.plot(timeTicks,cool_res["cool_dem"], color="black", linewidth = 3, label="Cooling demand")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))

    # Create second subplot: power balance
    plt.subplot(313, ylabel = 'Electrical power in MW', xlabel = xTitle)
    plt.stackplot(timeTicks, np.vstack(power_res_list), labels=power_labels, colors=power_color)
    plt.plot(timeTicks, power_res["power_dem"]+power_res["power_CC"]+power_res["power_EH"]+power_res["power_ASHP"]+power_res["ch_BAT"]+power_res["power_to_grid"], color="black", dashes=[3,3], linewidth = 3, label="Power to grid")
    plt.plot(timeTicks, power_res["power_dem"]+power_res["power_CC"]+power_res["power_EH"]+power_res["power_ASHP"]++power_res["ch_BAT"], linewidth = 3, label="BAT (charge)")
    plt.plot(timeTicks, power_res["power_dem"]+power_res["power_CC"]+power_res["power_EH"]+power_res["power_ASHP"], color=tech_color["power_ASHP"], linewidth = 3, label="ASHP demand")
    plt.plot(timeTicks, power_res["power_dem"]+power_res["power_CC"]+power_res["power_EH"], color=tech_color["power_EH"], linewidth = 3, label="EH demand")
    plt.plot(timeTicks, power_res["power_dem"]+power_res["power_CC"], color=tech_color["power_CC"], linewidth = 3, label="CC demand")
    plt.plot(timeTicks, power_res["power_dem"], color='black', linewidth = 3, label="Power demand")

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))

    plt.savefig(fname = save_name +".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1) #transparent = True,
#    plt.savefig(fname = save_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
#    print("Plot created: " + save_name +".png")
    plt.clf()
    plt.close()
    
    #%% Plots a time series for storages of abitrary length
def plot_interval_storage(M, save_name, xTitle):
    tech_color = get_tech_color()
    # Manipulate colors for storages for this plot
    tech_color["soc_BAT"] =      (0.749, 0.749, 0.749, 1)
    tech_color["soc_CTES"] =     (0.184, 0.459, 0.710, 0.8)
    tech_color["soc_TES"] =      (0.843, 0.059, 0.059, 0.8)
    
    # Transform data for plots
    sto_res = {}
    for device in ["soc_TES", "soc_CTES", "soc_BAT"]:    
        sto_res[device] = np.zeros(2*M[device].size)
        for t in range(M[device].size):
            sto_res[device][2*t:2*t+2] = [M[device][t], M[device][t]]
            
    # Create time ticks for x-axis
    timeTicks = [0]
    for t in range(M["soc_TES"].size):
        timeTicks.extend([timeTicks[-1] + 1])
        timeTicks.extend([timeTicks[-2] + 1])
    del timeTicks[-1]

    # Create figure
    plt.figure(figsize=(12, 9))
    plt.rcParams.update({'font.size': 14})

    # Create subplot: TES
    plt.subplot(311, ylabel = 'State of charge in MWh', xlabel = " ")
    plt.plot(timeTicks, sto_res["soc_TES"], color=tech_color["soc_TES"], linewidth=3, label="Heat thermal energy storage")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)
    
    # Create subplot: CTES
    plt.subplot(312, ylabel = 'State of charge in MWh', xlabel = " ")
    plt.plot(timeTicks, sto_res["soc_CTES"], color=tech_color["soc_CTES"], linewidth=3, label="Cold thermal energy storage")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)
    
    # Create subplot: BAT
    plt.subplot(313, ylabel = 'State of charge in MWh', xlabel = xTitle)
    plt.plot(timeTicks, sto_res["soc_BAT"], color=tech_color["soc_BAT"], linewidth=3, label="Battery")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)

    plt.savefig(fname = save_name +".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1) #transparent = True,
#    plt.savefig(fname = save_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
#    print("\nPlot created: " + save_name +".png\n")
    plt.clf()
    plt.close()

    
def get_tech_color():
    """
    This function defines a color for each device that is used.
    
    """
    tech_color = {}
    tech_color["BOI"] = (0.843, 0.059, 0.059, 0.8)
    tech_color["heat_BOI"] = tech_color["BOI"]
    tech_color["CHP"] = (0.137, 0.706, 0.196, 0.8)
    tech_color["heat_CHP"] = tech_color["CHP"]             
    tech_color["power_CHP"] = tech_color["CHP"]
    tech_color["CHP_GT"] = (0.667, 0.824, 0.549, 0.6)
    tech_color["heat_CHP_GT"] = tech_color["CHP_GT"]             
    tech_color["power_CHP_GT"] = tech_color["CHP_GT"]
    tech_color["EH"] = (0.961, 0.412, 0.412, 0.8)
    tech_color["heat_EH"] = tech_color["EH"]       
    tech_color["power_EH"] = tech_color["EH"]
    tech_color["ASHP"] = (0.0, 0.706, 0.804, 0.8)
    tech_color["heat_ASHP"] = tech_color["ASHP"]        
    tech_color["power_ASHP"] = tech_color["ASHP"]
    tech_color["HP_ww"] = (0.471, 0.843, 1.0, 0.8)
    tech_color["heat_HP_ww"] = tech_color["HP_ww"]  
    tech_color["power_HP_ww"] = tech_color["HP_ww"]
    tech_color["power_PV"] = (1.000, 0.725, 0.000, 0.8)
    tech_color["PV_curtail"] = (1.000, 0.725, 0.000, 0.3)
    tech_color["power_PV_fac"] = tech_color["power_PV"]
    tech_color["heat_STC"] = (0.922, 0.471, 0.039, 0.8)
    tech_color["STC_curtail"] = (0.922, 0.471, 0.039, 0.3)
    tech_color["power_WT"] = (0.098, 0.843, 0.588, 0.8)
    tech_color["WT_curtail"] = (0.098, 0.843, 0.588, 0.3)
    tech_color["power_HT"] = tech_color["power_WT"]
    tech_color["AC"] = (0.529, 0.706, 0.882, 0.8)
    tech_color["heat_AC"] = tech_color["AC"]
    tech_color["cool_AC"] = tech_color["AC"]
    tech_color["CC"] = (0.184, 0.459, 0.710, 0.8)
    tech_color["cool_CC"] = tech_color["CC"]      
    tech_color["power_CC"] = tech_color["CC"]
    tech_color["BAT"] = (0.482, 0.482, 0.482, 0.8)
    tech_color["ch_BAT"] = tech_color["BAT"] 
    tech_color["dch_BAT"] = tech_color["BAT"]
    tech_color["TES"] = (0.482, 0.482, 0.482, 0.8)
    tech_color["ch_TES"] = tech_color["TES"]           
    tech_color["dch_TES"] = tech_color["TES"]
    tech_color["CTES"] = (0.482, 0.482, 0.482, 0.8)
    tech_color["ch_CTES"] = tech_color["CTES"] 
    tech_color["dch_CTES"] = tech_color["CTES"]
    tech_color["H2_TANK"] = (0.482, 0.482, 0.482, 0.8)
    tech_color["ch_H2_TANK"] = tech_color["H2_TANK"] 
    tech_color["dch_H2_TANK"] = tech_color["H2_TANK"]
    tech_color["power_from_grid"] = (0.749, 0.749, 0.749, 1)
    tech_color["power_to_grid"] = (0.749, 0.749, 0.749, 1)
    tech_color["GEN"] = (0.02, 0.627, 0.627, 0.8)
    tech_color["power_GEN"] = tech_color["GEN"]
    tech_color["ELYZ"] = (0.706, 0.510, 0.843, 0.8)
    tech_color["power_ELYZ"] = tech_color["ELYZ"]
    tech_color["FC"] = (0.549, 0.294, 0.784, 0.8)
    tech_color["heat_FC"] = tech_color["FC"]
    tech_color["power_FC"] = tech_color["FC"]
    tech_color["CONV"] = (0.749, 0.749, 0.749, 1)
    
    return tech_color

