# -*- coding: utf-8 -*-
"""
Created on Sat Mar 03 20:41:18 2018

@author: mwi
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
import json
#from matplotlib2tikz import save as tikz_save
#from matplotlib.sankey import Sankey

def create_plots(heat, power, cool, soc, ch, dch, dem, time_steps, tau, dirResults, x, cap, devs, param, res_obj, plot_mode):

    # start/end day of each month
    startD = np.array([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
    endD = np.array([31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365])
    MonthTuple = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")

    h = {} # contains all 8760 time steps
    H = {} # help dicitionary
    d = {} # contains mean values for 365 days
    D = {} # help dicitionary
    M = {} # contains mean values for 12 months

    devList = ["BOI_h", "CHP_ICE_h", "CHP_GT_h", "EH_h", "HP_aw_h", "HP_ww_h", "FC_h", "STC", "TES_ch", "TES_dch", "AC_h", "PV", "PV_fac", "WT", "HT", "CHP_ICE_p", "CHP_GT_p", "GEN_p", "CC_p", 
               "EH_p", "HP_aw_p", "HP_ww_p", "FC_p", "ELYZ_p", "BAT_ch", "BAT_dch", "power_from_grid", "power_to_grid", "heat_dem", "CC_c", "AC_c", 
               "ITES_ch", "ITES_dch", "cool_dem", "power_dem_AC", "power_dem_DC", "STC_curtail", "PV_curtail", "PV_fac_curtail", "WT_curtail", "CONV_to_AC", "CONV_to_DC", "AC_to_CONV", "DC_to_CONV", 
               "TES", "ITES", "BAT", "H2_TANK"]  
               
    for device in devList:
        h[device] = np.zeros(8760)
        H[device] = {}
        d[device] = np.zeros(365)
        D[device] = {}
        M[device] = np.zeros(12)
        
    for t in time_steps:
        h["BOI_h"][t] = heat["BOI"][t].X
        h["CHP_ICE_h"][t] = heat["CHP_ICE"][t].X
        h["CHP_GT_h"][t] = heat["CHP_GT"][t].X
        h["EH_h"][t] = heat["EH"][t].X
        h["HP_aw_h"][t] = heat["HP_aw"][t].X
        h["HP_ww_h"][t] = heat["HP_ww"][t].X
        h["FC_h"][t] = heat["FC"][t].X
        h["STC"][t] = heat["STC"][t].X
        h["STC_curtail"][t] = devs["STC"]["heat"][t] * cap["STC"].X - h["STC"][t]
        h["TES_ch"][t] = ch["TES"][t].X
        h["TES_dch"][t] = dch["TES"][t].X
        h["AC_h"][t] = heat["AC"][t].X
        h["heat_dem"][t] = dem["heat"][t]
        h["CC_c"][t] = cool["CC"][t].X
        h["AC_c"][t] = cool["AC"][t].X
        h["ITES_ch"][t] = ch["ITES"][t].X
        h["ITES_dch"][t] = dch["ITES"][t].X
        h["cool_dem"][t] = dem["cool"][t]
        h["PV"][t] = power["PV"][t].X + power["PV_fac"][t].X
        h["PV_curtail"][t] = (devs["PV"]["power"][t] * cap["PV"].X - h["PV"][t]) + (devs["PV_fac"]["power"][t] * cap["PV_fac"].X - h["PV_fac"][t])
        h["PV_fac"][t] = power["PV_fac"][t].X
        h["WT"][t] = power["WT"][t].X + power["HT"][t].X
        h["WT_curtail"][t] = (devs["WT"]["power"][t] * cap["WT"].X - h["WT"][t]) + (devs["HT"]["power"][t] * cap["HT"].X - h["HT"][t])
        h["HT"][t] = power["HT"][t].X
        h["CHP_ICE_p"][t] = power["CHP_ICE"][t].X
        h["CHP_GT_p"][t] = power["CHP_GT"][t].X
        h["GEN_p"][t] = power["GEN"][t].X
        h["ELYZ_p"][t] = power["ELYZ"][t].X
        h["FC_p"][t] = power["FC"][t].X
        h["CC_p"][t] = power["CC"][t].X
        h["EH_p"][t] = power["EH"][t].X
        h["HP_aw_p"][t] = power["HP_aw"][t].X
        h["HP_ww_p"][t] = power["HP_ww"][t].X
        h["BAT_ch"][t] = ch["BAT"][t].X
        h["BAT_dch"][t] = dch["BAT"][t].X
        h["power_dem_AC"][t] = dem["power_AC"][t]
        h["power_dem_DC"][t] = dem["power_DC"][t]
        h["power_from_grid"][t] = power["from_grid"][t].X
        h["power_to_grid"][t] = power["to_grid"][t].X
        h["CONV_to_AC"][t] = power["CONV_to_AC"][t].X
        h["CONV_to_DC"][t] = power["CONV_to_DC"][t].X
        h["AC_to_CONV"][t] = power["AC_to_CONV"][t].X
        h["DC_to_CONV"][t] = power["DC_to_CONV"][t].X    
        h["TES"][t] = soc["TES"][t].X
        h["ITES"][t] = soc["ITES"][t].X
        h["BAT"][t] = soc["BAT"][t].X
        h["H2_TANK"][t] = soc["H2_TANK"][t].X
        
    # divide time series (8760 time steps) into daily (H), monthly (D) and yearly profiles (M)
    for device in devList:
        for k in range(365):
            H[device][k] = h[device][(k*24):(k*24+24)]
            d[device][k] = sum(h[device][(k*24):(k*24+24)])/24
    
        for m in range(12):
            D[device][m] = d[device][startD[m]:endD[m]]
            M[device][m] = sum(d[device][startD[m]:endD[m]])/(endD[m]-startD[m])

    dev_list_heat = ["BOI_h", "CHP_ICE_h", "CHP_GT_h", "EH_h", "HP_aw_h", "HP_ww_h", "FC_h", "STC", "TES_ch", "TES_dch", "AC_h", "heat_dem", "STC_curtail"]
    dev_list_cool = [ "CC_c", "AC_c", "ITES_ch", "ITES_dch", "cool_dem"]
    dev_list_power = ["PV", "WT", "HT", "CHP_ICE_p", "CHP_GT_p", "GEN_p", "CC_p", "EH_p", "HP_aw_p", "HP_ww_p", "FC_p", "ELYZ_p", "BAT_ch", "BAT_dch", "power_from_grid", "power_to_grid", "power_dem_AC", "power_dem_DC", "PV_curtail", "WT_curtail"]  
    heatDict = {}
    coolDict = {}
    powerDict = {}
    stoDict = {}
    
    #%% Create flow table
    if plot_mode["energy_flows"] == 1:
        save_energy_flows(h, time_steps, dirResults)
    
    #%% Plot costs, renewable share and emissions
    plot_costs(res_obj, param, dirResults)
    plot_renewable_share(res_obj, param, dirResults)
    plot_emissions(res_obj, param, dirResults)
    
    #%% Plot yearly profile
    if plot_mode["yearly"] == 1:
        
        for dev in dev_list_heat:
            heatDict[dev] = M[dev]
        for dev in dev_list_cool:
            coolDict[dev] = M[dev]  
        for dev in dev_list_power:
            powerDict[dev] = M[dev]            
        saveName = dirResults + "//Year_Profile"
        plot_interval(heatDict, coolDict, powerDict, saveName, "Month")
        saveName = dirResults + "//Year_Profile_Storage"
        plot_interval_storage(M, saveName, "Month")
    
    #%% Plot monthly profile
    if plot_mode["monthly"] == 1:
        
        for m in range(12):
            for dev in dev_list_heat:
                heatDict[dev] = D[dev][m]
            for dev in dev_list_cool:
                coolDict[dev] = D[dev][m]  
            for dev in dev_list_power:
                powerDict[dev] = D[dev][m]
            saveName = dirResults + "//" + str(m+1) + "_" + str(MonthTuple[m])
            plot_interval(heatDict, coolDict, powerDict, saveName, "Day")
            for dev in ["TES", "ITES", "BAT", "H2_TANK"]:
                stoDict[dev] = D[dev][m]  
            saveName = dirResults + "//" + str(m+1) + "_" + str(MonthTuple[m]) + "_Storage"
            plot_interval_storage(stoDict, saveName, "Day")

    #%% Plot daily profile
    if plot_mode["daily"] == 1:

        for d in range(365): # full year: range(365)
            month_name = (datetime.date(2018,1,1) + datetime.timedelta(days=d)).strftime("%b")
            month_num = (datetime.date(2018,1,1) + datetime.timedelta(days=d)).strftime("%m")
            day_num = (datetime.date(2018,1,1) + datetime.timedelta(days=d)).strftime("%d")
            # Create result folder for month
            if not os.path.exists(dirResults + "//" + str(month_num) + "_" + month_name):
                os.makedirs(dirResults + "//" + str(month_num) + "_" + month_name)
            for dev in dev_list_heat:
                heatDict[dev] = H[dev][d]
            for dev in dev_list_cool:
                coolDict[dev] = H[dev][d]  
            for dev in dev_list_power:
                powerDict[dev] = H[dev][d]
            saveName = dirResults + "//" + str(month_num) + "_" + month_name + "//" + month_name + "_" + str(day_num)
            plot_interval(heatDict, coolDict, powerDict, saveName, "Time [hours]")
            for dev in ["TES", "ITES", "BAT", "H2_TANK"]:
                stoDict[dev] = H[dev][d]
            saveName = dirResults + "//" + str(month_num) + "_" + month_name + "//" + month_name + "_" + str(day_num) + "_Storage"
            plot_interval_storage(stoDict, saveName, "Time [hours]")
            

    #%% Installed capacity plot
    if plot_mode["capacities"] == 1:
        
        capacity = {}
        load_factor = {}
        load_factor_key = {"BOI": "BOI_h", "CHP_ICE": "CHP_ICE_p", "CHP_GT": "CHP_GT_p", 
                           "GEN": "GEN_p", "EH": "EH_h", "HP_aw": "HP_aw_h", "HP_ww": "HP_ww_h",
                           "ELYZ": "ELYZ_p", "FC": "FC_p", "CC": "CC_c", "AC": "AC_c",
                           "PV": "PV", "PV_fac": "PV_fac", "STC": "STC", "WT": "WT", "HT": "HT"}
        
        for dev in ["BOI", "CHP_ICE", "CHP_GT", "GEN", "EH", "HP_aw", "HP_ww", "ELYZ", "FC", "CC", "AC", "PV", "PV_fac", "STC", "WT", "HT"]:
            capacity[dev] = cap[dev].X
            if capacity[dev] > 0:
                load_factor[dev] = h[load_factor_key[dev]].mean()/capacity[dev]
            else:
                load_factor[dev] = 0
        
        capacity["CONV"] = cap["CONV"].X
        load_factor["CONV"] = (h["AC_to_CONV"]+h["DC_to_CONV"]).mean()/capacity["CONV"]
            
        plot_capacity(capacity, load_factor, dirResults)

    #%% Device plot    
    if plot_mode["devices"] == 1:

        # heating
        plot_device("BOI", h["BOI_h"], dirResults)
        plot_device("EH", h["EH_h"], dirResults)
        plot_device("HP_aw", h["HP_aw_h"], dirResults)
        plot_device("HP_ww", h["HP_ww_h"], dirResults)
        plot_device("STC", h["STC"], dirResults)
        plot_device("heat_dem", h["heat_dem"], dirResults)
      
        # cooling
        plot_device("cool_dem", h["cool_dem"], dirResults)
        plot_device("CC", h["CC_c"], dirResults)
        plot_device("AC", h["AC_c"], dirResults)
      
        # power
        plot_device("WT", h["WT"], dirResults)
        plot_device("HT", h["HT"], dirResults)
        plot_device("PV", h["PV"], dirResults)
        plot_device("PV_fac", h["PV_fac"], dirResults)
        plot_device("CHP_ICE", h["CHP_ICE_p"], dirResults)
        plot_device("CHP_GT", h["CHP_GT_p"], dirResults)
        plot_device("GEN", h["GEN_p"], dirResults)
        plot_device("FC", h["FC_p"], dirResults)
        plot_device("ELYZ", h["ELYZ_p"], dirResults)
        plot_device("power_dem_AC", h["power_dem_AC"], dirResults)
        plot_device("power_dem_DC", h["power_dem_DC"], dirResults)
        plot_device("power_from_grid", h["power_from_grid"], dirResults)
        plot_device("power_to_grid", h["power_to_grid"], dirResults)
        plot_device("TES", h["TES"], dirResults)
        plot_device("ITES", h["ITES"], dirResults)
        plot_device("BAT", h["BAT"], dirResults)
        plot_device("H2_TANK", h["H2_TANK"], dirResults)
        
        plot_year_curve("BOI", h["BOI_h"], "Heating output in MW", dirResults)
        plot_year_curve("H2_TANK", h["H2_TANK"], "State of charge in MWh", dirResults)
        
def plot_year_curve(device, time_series, y_label, dirResults):
    compColor = get_compColor()
    # Manipulate colors for storages for this plot
    compColor["BAT"] =      (0.749, 0.749, 0.749, 1)
    compColor["ITES"] =     (0.184, 0.459, 0.710, 0.8)
    compColor["TES"] =      (0.843, 0.059, 0.059, 0.8)
    compColor["H2_TANK"] =  (0.549, 0.294, 0.784, 0.8)
    
    # Create figure
    plt.figure(figsize=(12, 9))
    plt.rcParams.update({'font.size': 14})

    # Create subplot: heat balance
    plt.subplot(311, ylabel = y_label, xlabel = "Hours")
    plt.plot(time_series, color=compColor[device])
    plt.xlim([0, 8760])

    plt.savefig(fname = dirResults + "//Year_plot_ " + device +".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1) #transparent = True,
    plt.savefig(fname = dirResults + "//Year_plot_ " + device +".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("\nPlot created: " + "Year_plot_ " + device +".png\n")
    plt.clf()
    plt.close()
    

    #%% plots a time series of abitrary length
def plot_interval(heat, cool, power, saveName, xTitle):
    compColor = get_compColor()
    label_dev = {"BOI_h": "Boiler",
                 "CHP_ICE_h": "ICE (CHP)",
                 "CHP_GT_h": "Gas turbine (CHP)",
                 "EH_h": "E-heater",
                 "HP_aw_h": "AS heat pump",
                 "HP_ww_h": "GS heat pump",
                 "FC_h": "Fuel cell",
                 "TES_dch": "HTES (discharge)",
                 "STC": "STC",
                 "STC_curtail": "STC (curtailed)",
                 "CC_c": "Comp. chiller",
                 "AC_c": "Abs. chiller",
                 "ITES_dch": "CTES (discharge)",
                 "CHP_ICE_p": "ICE (CHP)",
                 "CHP_GT_p": "Gas turbine",
                 "FC_p": "Fuel cell",
                 "GEN_p": "Generator",
                 "WT": "Wind",
                 "PV": "PV",
                 "power_from_grid": "Grid power",
                 "BAT_dch": "Battery (discharge)",
                 "PV_curtail": "PV (curtailed)",
                 "WT_curtail": "Wind (curtailed)",
                 }

    # Transform data for plots: heating
    heat_res = {}    
    heat_labels = []
    heat_res_list = []
    heat_color = []
    for device in ["BOI_h", "CHP_ICE_h", "CHP_GT_h", "EH_h", "HP_aw_h", "HP_ww_h", "FC_h", "TES_dch", "STC", "STC_curtail"]:
        heat_res[device] = np.zeros(2*heat[device].size)
        for t in range(heat[device].size):            
            heat_res[device][2*t:2*t+2] = [heat[device][t], heat[device][t]]
        heat_res_list.extend([heat_res[device].tolist()])
        heat_labels.append(label_dev[device])
        heat_color.extend([compColor[device]])    
    for device in ["heat_dem", "AC_h", "TES_ch"]:    
        heat_res[device] = np.zeros(2*heat[device].size)
        for t in range(heat[device].size):
            heat_res[device][2*t:2*t+2] = [heat[device][t], heat[device][t]]
            
    # Transform data for plots: cooling
    cool_res = {}    
    cool_labels = []
    cool_res_list = []
    cool_color = []
    for device in ["CC_c", "AC_c", "ITES_dch"]:
        cool_res[device] = np.zeros(2*cool[device].size)
        for t in range(cool[device].size):            
            cool_res[device][2*t:2*t+2] = [cool[device][t], cool[device][t]]
        cool_res_list.extend([cool_res[device].tolist()])
        cool_labels.append(label_dev[device])
        cool_color.extend([compColor[device]])    
    for device in ["cool_dem", "ITES_ch"]:    
        cool_res[device] = np.zeros(2*cool[device].size)
        for t in range(cool[device].size):
            cool_res[device][2*t:2*t+2] = [cool[device][t], cool[device][t]]

    # Transform data for plots: power
    power_res = {}    
    power_labels = []
    power_res_list = []
    power_color = []
    for device in ["CHP_ICE_p", "CHP_GT_p", "FC_p", "GEN_p", "WT", "PV", "power_from_grid", "BAT_dch", "PV_curtail", "WT_curtail"]:
        power_res[device] = np.zeros(2*power[device].size)
        for t in range(power[device].size):            
            power_res[device][2*t:2*t+2] = [power[device][t], power[device][t]]
        power_res_list.extend([power_res[device].tolist()])
        power_labels.append(label_dev[device])
        power_color.extend([compColor[device]])
    for device in ["power_dem_AC", "power_dem_DC", "CC_p", "EH_p", "ELYZ_p", "HP_aw_p", "HP_ww_p", "BAT_ch", "power_to_grid"]:    
        power_res[device] = np.zeros(2*power[device].size)
        for t in range(power[device].size):
            power_res[device][2*t:2*t+2] = [power[device][t], power[device][t]]

    # Create time ticks for x-axis
    timeTicks = [0]
    for t in range(heat["BOI_h"].size):
        timeTicks.extend([timeTicks[-1] + 1])
        timeTicks.extend([timeTicks[-2] + 1])
    del timeTicks[-1]

    # Create figure
    plt.figure(figsize=(12, 9))
    plt.rcParams.update({'font.size': 14})

    # Create subplot: heat balance
    plt.subplot(311, ylabel = 'Heating output in MW', xlabel = " ")
    plt.stackplot(timeTicks, np.vstack(heat_res_list), labels=heat_labels, colors=heat_color)
    plt.plot(timeTicks, heat_res["heat_dem"]+heat_res["AC_h"]+heat_res["TES_ch"], color=compColor["TES_ch"], linewidth = 3, label="HTES (charge)")
    plt.plot(timeTicks, heat_res["heat_dem"]+heat_res["AC_h"], color=compColor["AC_h"], linewidth = 3, label="AC demand")
    plt.plot(timeTicks, heat_res["heat_dem"], color="black", linewidth = 3, label="Heating demand")

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)

    # Create second subplot: cooling balance
    plt.subplot(312, ylabel = 'Cooling output in MW', xlabel = " ")
    plt.stackplot(timeTicks, np.vstack(cool_res_list), labels=cool_labels, colors=cool_color)
    plt.plot(timeTicks, cool_res["cool_dem"]+cool_res["ITES_ch"], color=compColor["ITES_ch"], linewidth = 3, label="CTES (charge)")
    plt.plot(timeTicks,cool_res["cool_dem"], color='black', linewidth = 3, label="Cooling demand")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))

    # Create second subplot: power balance
    plt.subplot(313, ylabel = 'Electrical power in MW', xlabel = xTitle)
    plt.stackplot(timeTicks, np.vstack(power_res_list), labels=power_labels, colors=power_color)
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"]+power_res["EH_p"]+power_res["HP_aw_p"]+power_res["HP_ww_p"]+power_res["ELYZ_p"]+power_res["BAT_ch"]+power_res["power_to_grid"], color="black", dashes=[3,3], linewidth = 3, label="Power to grid")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"]+power_res["EH_p"]+power_res["HP_aw_p"]+power_res["HP_ww_p"]+power_res["ELYZ_p"]+power_res["BAT_ch"], color=compColor["BAT_ch"], linewidth = 3, label="BAT (charge)")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"]+power_res["EH_p"]+power_res["HP_aw_p"]+power_res["HP_ww_p"]+power_res["ELYZ_p"], color=compColor["ELYZ_p"], linewidth = 3, label="Electrolyzer")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"]+power_res["EH_p"]+power_res["HP_aw_p"]+power_res["HP_ww_p"], color=compColor["HP_ww_p"], linewidth = 3, label="GSHP demand")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"]+power_res["EH_p"]+power_res["HP_aw_p"], color=compColor["HP_aw_p"], linewidth = 3, label="ASHP demand")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"]+power_res["EH_p"], color=compColor["EH_p"], linewidth = 3, label="EH demand")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"]+power_res["CC_p"], color=compColor["CC_p"], linewidth = 3, label="CC demand")
    plt.plot(timeTicks, power_res["power_dem_AC"]+power_res["power_dem_DC"], color='black', linewidth = 3, label="Power demand")

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))

    plt.savefig(fname = saveName +".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1) #transparent = True,
    plt.savefig(fname = saveName + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("\nPlot created: " + saveName +".png\n")
#    tikz_save("test.tex")
    plt.clf()
    plt.close()
    
    #%% plots a time series for storages of abitrary length
def plot_interval_storage(M, saveName, xTitle):
    compColor = get_compColor()
    # Manipulate colors for storages for this plot
    compColor["BAT"] =      (0.749, 0.749, 0.749, 1)
    compColor["ITES"] =     (0.184, 0.459, 0.710, 0.8)
    compColor["TES"] =      (0.843, 0.059, 0.059, 0.8)
    compColor["H2_TANK"] =  (0.549, 0.294, 0.784, 0.8)
    
    # Transform data for plots
    sto_res = {}
    for device in ["TES", "ITES", "BAT", "H2_TANK"]:    
        sto_res[device] = np.zeros(2*M[device].size)
        for t in range(M[device].size):
            sto_res[device][2*t:2*t+2] = [M[device][t], M[device][t]]
            
    # Create time ticks for x-axis
    timeTicks = [0]
    for t in range(M["TES"].size):
        timeTicks.extend([timeTicks[-1] + 1])
        timeTicks.extend([timeTicks[-2] + 1])
    del timeTicks[-1]

    # Create figure
    plt.figure(figsize=(12, 9))
    plt.rcParams.update({'font.size': 14})

    # Create subplot: TES
    plt.subplot(311, ylabel = 'State of charge in MWh', xlabel = " ")
    plt.plot(timeTicks, sto_res["TES"], color=compColor["TES"], linewidth=3, label="Heat thermal energy storage")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)
    
    # Create subplot: ITES
    plt.subplot(312, ylabel = 'State of charge in MWh', xlabel = " ")
    plt.plot(timeTicks, sto_res["ITES"], color=compColor["ITES"], linewidth=3, label="Cold thermal energy storage")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)
    
    # Create subplot: BAT and H2_TANK
    plt.subplot(313, ylabel = 'State of charge in MWh', xlabel = xTitle)
    plt.plot(timeTicks, sto_res["BAT"], color=compColor["BAT"], linewidth=3, label="Battery")
    plt.plot(timeTicks, sto_res["H2_TANK"], color=compColor["H2_TANK"], linewidth=3, label="Hydrogen tank")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
    plt.xticks(np.arange(min(timeTicks), max(timeTicks)+1, 1))
    plt.xlim(min(timeTicks), max(timeTicks))
    plt.tight_layout(h_pad=6)

    plt.savefig(fname = saveName +".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1) #transparent = True,
    plt.savefig(fname = saveName + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("\nPlot created: " + saveName +".png\n")
    plt.clf()
    plt.close()

#%% plots comprehensive operation information for devices
def plot_device(device, time_series, dirResults):
    
    monthInfoAcc = {0: 1, 1: 31, 2: 59, 3: 90, 4: 120, 5: 151, 6:181, 7: 212, 8:243, 9:273, 10:304, 11:334, 12:365}
    monthInfoMid = {0: 15.5, 1: 45, 2: 74.5, 3: 105, 4: 135.5, 5: 166, 6: 196.5, 7: 227.5, 8: 258, 9: 288.5, 10: 319, 11: 349.5}
    MonthTuple = ("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")
    MonthList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    device_name = {"BOI": "Boiler", "CHP_ICE": "CHP (internal combustion engine)", "CHP_GT": "CHP (gas turbine)", "GEN": "Backup generator", "EH": "Electric heater", "HP_aw": "Heat pump (air/water)", 
                   "HP_ww": "Heat pump (water/water)", "CC": "Compression chiller", "AC": "Absorption chiller", "PV": "Photovoltaic (roof-top)", "PV_fac": "Photovoltaic (facade)", 
                   "WT": "Wind turbine", "HT": "Helix turbine", "STC": "Solar thermal collector", "heat_dem": "Heating demand", "cool_dem": "Cooling demand",
                   "power_dem_AC": "Power demand (AC grid)", "power_dem_DC": "Power demand (DC grid)", "power_from_grid": "Electric power from grid", "power_to_grid": "Electric power to grid",
                   "FC": "Fuel Cell", "ELYZ": "Electrolyzer", "TES": "Heat thermal energy storage", "ITES": "Cold thermal energy storage", "BAT": "Battery", "H2_TANK": "Hydrogen tank"}

    if device in ["BOI", "EH", "HP_ww", "HP_aw", "STC", "heat_dem"]:
        cmap_color = "Reds"
        box_color = "lightsalmon"
        y_label = "Heating output in MW"
        
    elif device in ["CC", "AC", "cool_dem"]:
        cmap_color = "Blues"
        box_color = "lightblue"    
        y_label = "Cooling output in MW"
        
    elif device in ["WT", "HT", "PV", "PV_fac", "CHP_ICE", "CHP_GT", "GEN", "FC", "ELYZ", "power_dem_AC", "power_dem_DC", "power_from_grid", "power_to_grid", "H2_TANK", "BAT"]:
        cmap_color = "Greys"
        box_color = "lightgray"   
        y_label = "Electrical power in MW"
        
    elif device in ["TES"]:
        cmap_color = "Reds"
        box_color = "lightsalmon"
        y_label = "State of charge in MWh"
        
    elif device in ["ITES"]:
        cmap_color = "Blues"
        box_color = "lightblue"    
        y_label = "State of charge in MWh"
        
    elif device in ["BAT", "H2_TANK"]:
        cmap_color = "Greys"
        box_color = "lightgray" 
        y_label = "State of charge in MWh"
        
    # rewrite time series dict in two-dimensional dict
    data = np.zeros([24,365])
    for t in range(8760):
        data[23-(t % 24), t // 24] = time_series[t]
    
    fig = plt.figure(figsize=(10,10))
    plt.rc('font', size=15)
    
    # First plot: Yearly profile
    ax = fig.add_subplot(311)
    im = ax.imshow(data, interpolation='none', extent=[0,365,0,24], aspect=4, cmap=cmap_color)
    cbar = fig.colorbar(im, orientation="horizontal", shrink=0.7, pad=0.2, aspect=40)
    cbar.set_label(y_label)
    plt.yticks([0, 6, 12, 18, 24])
    plt.xticks([monthInfoMid[k] for k in range(12)], MonthTuple)
    plt.title(str(device_name[device] + " (" + device + ")"))
    
    # Second plot: Daily profile
    fig.add_subplot(312, ylabel=y_label)
    plt.boxplot(np.transpose(np.flip(data,0)),0,'',whis="range",patch_artist=True,boxprops=dict(facecolor=box_color),medianprops=dict(color="black"))
    plt.title("Daily profile")
    
    # Third plot: Monthly profile
    fig.add_subplot(313, ylabel=y_label)
    dataMonth = {}
    for k in range(12):
        dataMonth[k] = np.concatenate((data[:,monthInfoAcc[k]-1:monthInfoAcc[k+1]-1]), 0)
    plt.boxplot([dataMonth[k] for k in range(12)],0,'',whis="range",patch_artist=True,boxprops=dict(facecolor=box_color),medianprops=dict(color="black"))
    plt.xticks(MonthList, MonthTuple)
    plt.title("Seasonal profile")
    plt.tight_layout()
    
    # Save plot
    file_name = dirResults + "//Device_stats_" + device
    plt.savefig(file_name + ".png", dpi = 400, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 400, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()

def plot_capacity(cap, load_factor, dirResults):
    compColor = get_compColor()
    color_list = [compColor[dev] for dev in cap.keys()]
    cap_list = [round(cap[dev],3) for dev in cap.keys()]
    print(cap_list)
    load_factor_list = [round(load_factor[dev],3) for dev in load_factor.keys()]
    
    # Create new figure
    fig = plt.figure(figsize=(10,5))
    plt.rc('font', size=15)
    fig.add_subplot(211, ylabel="Capacity in MW")
    plt.bar(range(len(cap.keys())), cap_list, 1, color=color_list, linewidth=1, edgecolor='black')
    plt.xticks(range(len(cap.keys())), cap.keys())
    
    plt.xlim([-0.5,len(cap.keys())-0.5])
    plt.xticks(fontsize=10)
    blank_row = ["" for i in range(len(cap_list))]
    data_table = plt.table(cellText=[blank_row,blank_row,blank_row,cap_list,blank_row,load_factor_list],
                          cellLoc='center',
                          rowLabels=["","","","Capacity","","Load factor"],
                          loc='bottom')
    
    table_props = data_table.properties()
    table_cells = table_props['child_artists']
    for cell in table_cells:
        for key, cell in data_table.get_celld().items():
            cell.set_linewidth(0)
    
    # Save plot
    file_name = dirResults + "//Installed_capacity"
    plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()
    
    
def save_pareto_points(all_sol, obj_1, obj_2, dirResults):
    
    fout = dirResults + "//Pareto_Points.csv"
    fo = open(fout, "w")
    # Write header
    for obj in all_sol[0].keys():
            fo.write(obj + ",")
    fo.write(str("\n"))
    
    # Write solution
    for point in range(len(all_sol)):
        for obj in all_sol[point].keys():
            fo.write(str(all_sol[point][obj]) + ",")
        
        fo.write(str("\n"))
    fo.close()
    print("Saved pareto points in '" + fout + "' successfully.")
    
def plot_pareto_curve(all_sol, obj_1, obj_2, dirResults):
    
    scale = {"tac": 1000, 
             "co2_onsite": 1,
             "co2_net": 1,
             "co2_gross": 1,
             "invest": 1000,
             "power_from_grid": 1000,
             "net_power_from_grid": 1000,
             }

    axis_label = {"tac": "Total annual cost [Mio. EUR/a]", 
                  "co2_onsite": "CO2 emissions [t/a]",
                  "co2_net": "CO2 emissions [t/a]",
                  "co2_gross": "CO2 emissions [t/a]",
                  "invest": "Investment [Mio. EUR]",
                  "power_from_grid": "Electricity from grid [GWh/a]",
                  "net_power_from_grid": "Net electricity from grid [GWh/a]",
                  }
    
    plt.figure(figsize=(7,5))
    obj_1_list = [all_sol[k][obj_1] / scale[obj_1] for k in range(len(all_sol))]
    obj_2_list = [all_sol[k][obj_2] / scale[obj_2] for k in range(len(all_sol))]
    ax = plt.gca()
    ax.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.scatter(obj_1_list, obj_2_list, marker="o")
    # Basic plot modifications
    plt.rc('font', size=15)
    plt.xlabel(axis_label[obj_1])
    plt.ylabel(axis_label[obj_2])
    #plt.ticklabel_format(style='sci', axis='x', scilimits=(0,1000))
    
    # Save plot
    file_name = dirResults + "//Pareto_curve.png"
    plt.savefig(file_name +".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()
    
def plot_pareto_devices(all_sol, obj_1, obj_2, dirResults):
    """
    This function plots device capacities along the pareto curve.
    
    """
    
    label_dev = {"BOI": "Boiler",
                 "CHP_ICE": "ICE (CHP)",
                 "CHP_GT": "Gas turbine (CHP)",
                 "EH": "E-heater",
                 "HP_aw": "AS heat pump",
                 "HP_ww": "GS heat pump",
                 "FC": "Fuel cell",
                 "TES": "Heat storage",
                 "STC": "STC",
                 "CC": "Comp. chiller",
                 "AC": "Abs. chiller",
                 "ITES": "Cold storage",
                 "GEN": "Back-up generator",
                 "WT": "Wind turbine",
                 "HT": "Helix turbine",
                 "PV": "PV (roof)",
                 "PV_fac": "PV (facade)", 
                 "power_from_grid": "Grid power",
                 "BAT": "Battery",
                 "CONV": "Converter",
                 "H2_TANK": "Hydrogen tank",
                 "ELYZ": "Electrolyzer",
                 }
    
    compColor = get_compColor()
    # Manipulate colors for storages for this plot
    compColor["BAT"] =      (0.749, 0.749, 0.749, 1)
    compColor["ITES"] =     (0.184, 0.459, 0.710, 0.8)
    compColor["TES"] =      (0.843, 0.059, 0.059, 0.8)
    compColor["H2_TANK"] =  (0.549, 0.294, 0.784, 0.8)
    compColor["PV_fac"] =   (1.000, 0.85,  0.25,  0.9)
    compColor["HT"] =       (0.2,   0.95,  0.65,  0.9)
    
    # Create figure
    width = 0.7
    device_list = {}
    device_list["dev"] = ["BOI", "CHP_ICE", "CHP_GT", "EH", "HP_aw", "HP_ww", "AC", "CC", "PV", "PV_fac", "STC", "CONV", "GEN", "ELYZ", "FC", "WT", "HT"]
    device_list["sto_dev"] = ["TES", "ITES", "BAT", "H2_TANK"]

    obj_label = {"tac": "Cost optimum", 
                  "co2_onsite": "CO2 optimum",
                  "co2_net": "CO2 optimum",
                  "co2_gross": "CO2 optimum",
                  "invest": "Investment minimum",
                  "power_from_grid": "Minimum electricity from grid",
                  "net_power_from_grid": "Minimum electricity",
                  }

    y_label = {"dev": "Cumulative capacity [MW]", "sto_dev": "Cumulative storage capacity [MWh]"}
    file_name = {"dev": dirResults + "//Pareto_devices.png", "sto_dev": dirResults + "//Pareto_storage_devices.png"}
    all_sol_sorted = sorted(all_sol, key=lambda k: k['tac']) 
    num_sol = len(all_sol_sorted)
    res_list = {}
    legend_list = {}
    color_list = {}
    col_nr = {"dev": 3,
              "sto_dev": 4,
              }
    for dev_type in ["dev", "sto_dev"]:
        plt.figure(figsize=(10, 5))
        plt.rcParams.update({'font.size': 14})
        res_list[dev_type] = []
        legend_list[dev_type] = []
        color_list[dev_type] = []
        for key in all_sol_sorted[0].keys():
            if key in device_list[dev_type]:
                legend_list[dev_type].append(label_dev[key])
                color_list[dev_type].append(compColor[key])
                res_list[dev_type].append([])
                for sol in range(len(all_sol_sorted)):
                    res_list[dev_type][len(res_list[dev_type])-1].append(all_sol_sorted[sol][key])
                    
        plt.bar(np.arange(num_sol), res_list[dev_type][0], width, color=color_list[dev_type][0])
        list_prev = [0 for k in range(len(res_list[dev_type][0]))]
        for dev in range(1,len(res_list[dev_type]),1):
            plt.bar(np.arange(num_sol), res_list[dev_type][dev], width, color=color_list[dev_type][dev], bottom=[sum(x) for x in zip(list_prev, res_list[dev_type][dev-1])])
            list_prev = [sum(x) for x in zip(list_prev, res_list[dev_type][dev-1])]
        plt.ylabel(y_label[dev_type])
        # Create x-label
        x_label_list = []
        x_label_list.append("\n" + obj_label[obj_1])
        for k in range(3,num_sol+1,1):
            x_label_list.append(k-2)
        x_label_list.append("\n" + obj_label[obj_2])
        plt.xticks(np.arange(num_sol), x_label_list)
        plt.legend(legend_list[dev_type], bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=col_nr[dev_type], mode="expand", borderaxespad=0.)
        # Save plot
        plt.savefig(file_name[dev_type] + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
        plt.savefig(file_name[dev_type] + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
        print("Created plot '" + file_name[dev_type] + "' successfully.")
        plt.clf()
        plt.close()
    
    
def plot_costs(res_obj, param, dirResults):
    # invest, om, gas costs, elec price, revenue grid
    elec_costs = res_obj["power_from_grid"] * param["price_el"]
    elec_revenue = (res_obj["power_from_grid"] - res_obj["net_power_from_grid"]) * param["revenue_feed_in"]
    gas_costs = param["price_gas"] * (res_obj["co2_onsite"] / param["gas_CO2_emission"]) 
    om_cost = res_obj["tac"] - res_obj["invest"] - gas_costs - elec_costs + elec_revenue
       
    # With feed-in revenue
    fig1, ax1 = plt.subplots(figsize=(10,5))
    plt.rcParams.update({'font.size': 14})
    cost_data = [res_obj["invest"], om_cost, gas_costs, elec_costs, elec_revenue]
    patches, texts = plt.pie(cost_data, pctdistance=1.2)
    plt.legend(patches, ["Investment", "Operation & Maintenance", "Gas costs", "Electricity costs", "Feed-in revenue"], bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax1.axis('equal')
    file_name = dirResults + "//Costs_with_feed-in.png"
    plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()
    
    # Without feed-in revenue
    fig1, ax1 = plt.subplots(figsize=(10,5))
    plt.rcParams.update({'font.size': 14})
    cost_data = [res_obj["invest"], om_cost, gas_costs, elec_costs]
    patches, texts = plt.pie(cost_data, pctdistance=1.2)
    plt.legend(patches, ["Investment", "Operation & Maintenance", "Gas costs", "Electricity costs"], bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax1.axis('equal')
    file_name = dirResults + "//Costs.png"
    plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()
    # Write further information in txt-file
    sum_costs = res_obj["invest"] + om_cost + gas_costs + elec_costs
    with open(dirResults + "\Costs.txt", "w") as text_file:
        text_file.write("Invest: " + str(round(res_obj["invest"],6)) + " (" + str(res_obj["invest"]/sum_costs) + ")\n")
        text_file.write("O&M: " + str(round(om_cost,6)) + " (" + str(om_cost/sum_costs) + ")\n")
        text_file.write("Gas: " + str(round(gas_costs,6)) + " (" + str(gas_costs/sum_costs) + ")\n")
        text_file.write("Electricity: " + str(round(elec_costs,6)) + " (" + str(elec_costs/sum_costs) + ")\n")
        text_file.write("Electricity (feed-in): " + str(round(elec_revenue,6)))
    
    
def plot_renewable_share(res_obj, param, dirResults):
    gas = res_obj["co2_onsite"] / param["gas_CO2_emission"]
    fig1, ax1 = plt.subplots(figsize=(10,5))
    plt.rcParams.update({'font.size': 14})
    cost_data = [gas, res_obj["power_from_grid"], res_obj["renewables_abs"]]
    patches, texts = plt.pie(cost_data, pctdistance=1.2)
    plt.legend(patches, ["Gas", "Electricity", "Renewables"], bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax1.axis('equal')
    file_name = dirResults + "//Energy_ressources"
    plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()
    # Write further information in txt-file
    sum_ressources = gas + res_obj["power_from_grid"] + res_obj["renewables_abs"]
    with open(dirResults + "\Energy_ressources.txt", "w") as text_file:
        text_file.write("Gas: " + str(round(gas,6)) + " (" + str(gas/sum_ressources) + ")\n")
        text_file.write("Electricity: " + str(round(res_obj["power_from_grid"],6)) + " (" + str(res_obj["power_from_grid"]/sum_ressources) + ")\n")
        text_file.write("Renewables: " + str(round(res_obj["renewables_abs"],6)) + " (" + str(res_obj["renewables_abs"]/sum_ressources) + ")\n")
    
    
def plot_emissions(res_obj, param, dirResults):
    onsite = res_obj["co2_onsite"]
    grid = res_obj["co2_gross"] - res_obj["co2_onsite"]
    fig1, ax1 = plt.subplots(figsize=(10,5))
    plt.rcParams.update({'font.size': 14})
    cost_data = [onsite, grid]
    patches, texts = plt.pie(cost_data, pctdistance=1.2)
    plt.legend(patches, ["On-site emissions", "Implicit emissions (grid)"], bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax1.axis('equal')
    file_name = dirResults + "//Energy_emissions"
    plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
    plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
    print("Created plot '" + file_name + "' successfully.")
    plt.clf()
    plt.close()
    # Write further information in txt-file
    sum_emissions = onsite + grid
    with open(dirResults + "\Energy_emissions.txt", "w") as text_file:
        text_file.write("Onsite: " + str(round(onsite,6)) + " (" + str(onsite/sum_emissions) + ")\n")
        text_file.write("Grid: " + str(round(grid,6)) + " (" + str(grid/sum_emissions) + ")\n")


    
def get_compColor():
    """
    This function defines a color for each device that is used for plots.
    
    """
    
    compColor = {}
    compColor["BOI"] = (0.843, 0.059, 0.059, 0.8)
    compColor["BOI_h"] = compColor["BOI"]
    compColor["CHP_ICE"] = (0.137, 0.706, 0.196, 0.8)
    compColor["CHP_ICE_h"] = compColor["CHP_ICE"]             
    compColor["CHP_ICE_p"] = compColor["CHP_ICE"]
    compColor["CHP_GT"] = (0.667, 0.824, 0.549, 0.6)
    compColor["CHP_GT_h"] = compColor["CHP_GT"]             
    compColor["CHP_GT_p"] = compColor["CHP_GT"]
    compColor["EH"] = (0.961, 0.412, 0.412, 0.8)
    compColor["EH_h"] = compColor["EH"]       
    compColor["EH_p"] = compColor["EH"]
    compColor["HP_aw"] = (0.0, 0.706, 0.804, 0.8)
    compColor["HP_aw_h"] = compColor["HP_aw"]        
    compColor["HP_aw_p"] = compColor["HP_aw"]
    compColor["HP_ww"] = (0.471, 0.843, 1.0, 0.8)
    compColor["HP_ww_h"] = compColor["HP_ww"]  
    compColor["HP_ww_p"] = compColor["HP_ww"]
    compColor["PV"] = (1.000, 0.725, 0.000, 0.8)
    compColor["PV_curtail"] = (1.000, 0.725, 0.000, 0.3)
    compColor["PV_fac"] = compColor["PV"]
    compColor["STC"] = (0.922, 0.471, 0.039, 0.8)
    compColor["STC_curtail"] = (0.922, 0.471, 0.039, 0.3)
    compColor["WT"] = (0.098, 0.843, 0.588, 0.8)
    compColor["WT_curtail"] = (0.098, 0.843, 0.588, 0.3)
    compColor["HT"] = compColor["WT"]
    compColor["AC"] = (0.529, 0.706, 0.882, 0.8)
    compColor["AC_h"] = compColor["AC"]
    compColor["AC_c"] = compColor["AC"]
    compColor["CC"] = (0.184, 0.459, 0.710, 0.8)
    compColor["CC_c"] = compColor["CC"]      
    compColor["CC_p"] = compColor["CC"]
    compColor["BAT"] = (0.482, 0.482, 0.482, 0.8)
    compColor["BAT_ch"] = compColor["BAT"] 
    compColor["BAT_dch"] = compColor["BAT"]
    compColor["TES"] = (0.482, 0.482, 0.482, 0.8)
    compColor["TES_ch"] = compColor["TES"]           
    compColor["TES_dch"] = compColor["TES"]
    compColor["ITES"] = (0.482, 0.482, 0.482, 0.8)
    compColor["ITES_ch"] = compColor["ITES"] 
    compColor["ITES_dch"] = compColor["ITES"]
    compColor["H2_TANK"] = (0.482, 0.482, 0.482, 0.8)
    compColor["H2_TANK_ch"] = compColor["H2_TANK"] 
    compColor["H2_TANK_dch"] = compColor["H2_TANK"]
    compColor["power_from_grid"] = (0.749, 0.749, 0.749, 1)
    compColor["power_to_grid"] = (0.749, 0.749, 0.749, 1)
    compColor["GEN"] = (0.02, 0.627, 0.627, 0.8)
    compColor["GEN_p"] = compColor["GEN"]
    compColor["ELYZ"] = (0.706, 0.510, 0.843, 0.8)
    compColor["ELYZ_p"] = compColor["ELYZ"]
    compColor["FC"] = (0.549, 0.294, 0.784, 0.8)
    compColor["FC_h"] = compColor["FC"]
    compColor["FC_p"] = compColor["FC"]
    compColor["CONV"] = (0.749, 0.749, 0.749, 1)
    
    return compColor

def save_energy_flows(h, time_steps, dirResults):
     
    sum_distr = {}
    heat_sources = ["BOI_h", "CHP_ICE_h", "CHP_GT_h", "EH_h", "HP_aw_h", "HP_ww_h", "FC_h", "STC", "TES_dch"]
    cool_sources = ["CC_c", "AC_c", "ITES_dch"]
    elec_sources = ["WT", "HT", "CHP_ICE_p", "CHP_GT_p", "power_from_grid", "GEN_p", "PV", "PV_fac", "BAT_dch", "FC_p"]
    compColor = get_compColor()
    
    consum = {}
    # Heating
    consum["heat"] = {}
    for t in time_steps:
        # sum heat consumption for every time step as fraction
        heat_sinks = ["heat_dem", "TES_ch", "AC_h"]
        consum["heat"][t] = np.array([h[k][t] for k in heat_sinks])
        if sum(consum["heat"][t]) == 0:
            consum["heat"][t] = np.zeros(len(heat_sinks))
        else:
            consum["heat"][t] = consum["heat"][t] / sum(consum["heat"][t])
    
    for dev in heat_sources:
        sum_distr[dev] = np.zeros(len(heat_sinks))
        for t in time_steps:
            # only boiler: ch, demand, ac
            sum_distr[dev] = sum_distr[dev] + h[dev][t] * consum["heat"][t]
 
    # Cooling
    consum["cool"] = {}
    for t in time_steps:
        # sum cooling consumption for every time step as fraction
        cool_sinks = ["cool_dem", "ITES_ch"]
        consum["cool"][t] = np.array([h[k][t] for k in cool_sinks])
        if sum(consum["cool"][t]) == 0:
            consum["cool"][t] = np.zeros(len(cool_sinks))
        else:
            consum["cool"][t] = consum["cool"][t] / sum(consum["cool"][t])
    
    for dev in cool_sources:
        sum_distr[dev] = np.zeros(len(cool_sinks))
        for t in time_steps:
            sum_distr[dev] = sum_distr[dev] + h[dev][t] * consum["cool"][t]
            
    # Electricity
    consum["elec"] = {}
    for t in time_steps:
        # sum electricity consumption for every time step as fraction
        h["power_dem"] = h["power_dem_DC"] + h["power_dem_AC"]
        elec_sinks = ["power_dem", "power_to_grid", "EH_p", "HP_aw_p", "HP_ww_p", "CC_p", "BAT_ch", "ELYZ_p"]
        consum["elec"][t] = np.array([h[k][t] for k in elec_sinks])
        if sum(consum["elec"][t]) == 0:
            consum["elec"][t] = np.zeros(len(elec_sinks))
        else:
            consum["elec"][t] = consum["elec"][t] / sum(consum["elec"][t])
    
    for dev in elec_sources:
        sum_distr[dev] = np.zeros(len(elec_sinks))
        for t in time_steps:
            sum_distr[dev] = sum_distr[dev] + h[dev][t] * consum["elec"][t]  
    
    # Create plots: heat
    sources_color = [compColor[dev] for dev in heat_sources]    
    for k in range(len(consum["heat"][0])):
        fig1, ax1 = plt.subplots(figsize=(10,5))
        plt.rcParams.update({'font.size': 14})
        heat_dem_sources = [float(sum_distr[dev][k]) for dev in heat_sources]
        patches, texts, hj = plt.pie(heat_dem_sources, colors=sources_color, autopct="%1.1f%%", pctdistance=1.2)
        plt.legend(patches, heat_sources, bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        ax1.axis('equal')
        file_name = dirResults + "//Supply_" + heat_sinks[k]
        plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
        plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
        print("Created plot '" + file_name + "' successfully.")
        plt.clf()
        plt.close()
    
    # Create plots: cooling
    sources_color = [compColor[dev] for dev in cool_sources]    
    for k in range(len(consum["cool"][0])):
        fig1, ax1 = plt.subplots(figsize=(10,5))
        plt.rcParams.update({'font.size': 14})
        cool_dem_sources = [float(sum_distr[dev][k]) for dev in cool_sources]
        patches, texts, hj = plt.pie(cool_dem_sources, colors=sources_color, autopct="%1.1f%%", pctdistance=1.2)
        plt.legend(patches, cool_sources, bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        ax1.axis('equal')
        file_name = dirResults + "//Supply_" + cool_sinks[k]
        plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
        plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
        print("Created plot '" + file_name + "' successfully.")
        plt.clf()
        plt.close()
        
    # Create plots: electricity
    sources_color = [compColor[dev] for dev in elec_sources]    
    for k in range(len(consum["elec"][0])):
        fig1, ax1 = plt.subplots(figsize=(10,5))
        plt.rcParams.update({'font.size': 14})
        elec_dem_sources = [float(sum_distr[dev][k]) for dev in elec_sources]
        patches, texts, hj = plt.pie(elec_dem_sources, colors=sources_color, autopct="%1.1f%%", pctdistance=1.2)
        plt.legend(patches, elec_sources, bbox_to_anchor=(0., -0.25, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0.)
        ax1.axis('equal')
        file_name = dirResults + "//Supply_" + elec_sinks[k]
        plt.savefig(file_name + ".png", dpi = 200, format = "png", bbox_inches="tight", pad_inches=0.1)
        plt.savefig(file_name + ".pdf", dpi = 200, format = "pdf", bbox_inches="tight", pad_inches=0.1)
        print("Created plot '" + file_name + "' successfully.")
        
        plt.clf()
        plt.close()
        
    #%% Write in csv
    fout = dirResults + "//Energy_flow.csv"
    fo = open(fout, "w")
    fo.write("Heat suppliers, heat_dem, TES_ch, AC_h\n")
    for dev in heat_sources:
        helpList = [sum_distr[dev][k] for k in range(len(sum_distr[dev]))]
        helpList_split = str(helpList).strip('[]')
        fo.write(dev + "," + str(helpList_split) + "\n")
        
    fo.write("\nCooling suppliers, cool_dem, ITES_ch\n")
    for dev in cool_sources:
        helpList = [sum_distr[dev][k] for k in range(len(sum_distr[dev]))]
        helpList_split = str(helpList).strip('[]')
        fo.write(dev + "," + str(helpList_split) + "\n")
        
    fo.write("\nElectricity suppliers, power_dem (AC+DC), power_to_grid, EH_p, HP_aw_p, HP_ww_p, CC_p, BAT_ch, ELYZ_p\n")
    for dev in elec_sources:
        helpList = [sum_distr[dev][k] for k in range(len(sum_distr[dev]))]
        helpList_split = str(helpList).strip('[]')
        fo.write(dev + "," + str(helpList_split) + "\n")
        
    fo.close()
    print("Saved energy flow data in '" + fout + "' successfully.")
    
    #%% Create sankey plots
    
    # AC (Absorption chiller)
#    plt.subplots(figsize=(10,5))
#    plt.axis("off")
#    sankey_scale = 1/(sum(sum_distr[k][2] for k in ["BOI_h", "CHP_ICE_h", "HP_ww_h", "TES_dch"]))
#    Sankey(flows=[sum_distr["BOI_h"][2], sum_distr["CHP_ICE_h"][2], sum_distr["HP_ww_h"][2], sum_distr["TES_dch"][2], (-1)*sum_distr["AC_c"][0], (-1)*sum_distr["AC_c"][1]], 
#           labels=["Boiler", "CHP (ICE)", "HP (w/w)", "TES", "Cooling\ndemand", "Ice\nstorage"], orientations=[1, 0, -1, -1, 0,-1], 
#           scale=sankey_scale, shoulder=0, gap=0.8, unit=" MWh", offset=0.5, head_angle=120, margin=2, trunklength=2, ax=ax1).finish()
#    plt.show()
#    plt.title("Absorption chiller")