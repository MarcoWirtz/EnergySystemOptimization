# -*- coding: utf-8 -*-
"""

Author: Marco Wirtz, Institute for Energy Efficient Buildings and Indoor Climate, RWTH Aachen University, Germany

Created: 01.09.2018

"""

import numpy as np
import pandas as pd
import math
import sun

def load_params():
    """
    Returns technical and economic parameter for optmization model.
    """

    # Set path to input files
    path_weather_file = "input_data/CHN_Shanghai.Shanghai.583670_IWEC.csv"
    path_heating_load = "input_data/heating.csv"
    path_cooling_load = "input_data/cooling.csv"
    path_power_load   = "input_data/electicity.csv"

    # Load weather file
    weather_df = pd.read_csv(path_weather_file)
    weather_dict = weather_df.to_dict()

    #%% LOADS
    dem = {}

    # load time series as numpy array
    dem["heat"] = np.loadtxt(open(path_heating_load, "rb"), delimiter=",", usecols=(1)) / 1000000         # MW, heating load
    dem["cool"] = np.loadtxt(open(path_cooling_load, "rb"), delimiter=",", usecols=(1)) / 1000000         # MW, cooling load
    dem["power"] = np.loadtxt(open(path_power_load, "rb"), delimiter=",", usecols=(1)) / 1000000          # MW, electrical load grid

    # Improve numeric by deleting very small loads
    eps = 0.01 # MW
    for load in ["power", "heat", "cool"]:
        for k in range(len(dem[load])):
           if dem[load][k] < eps:
              dem[load][k] = 0


    #%% ECONOMIC PARAMETER
    param = {"interest_rate":  0.05,        # ---,          interest rate
             "observation_time": 20.0,      # a,            project lifetime
             "price_gas": 0.0435,           # kEUR/MWh,     natural gas price
             "price_el": 0.106,             # kEUR/MWh,     electricity price (grid)
             "revenue_feed_in": 0.055,      # kEUR/MWh,     feed-in tariff (electricity)
             "gas_CO2_emission": 0.2,       # t_CO2/MWh,    specific CO2 emissions (natural gas)
             "grid_CO2_emission": 0.657,    # t_CO2/MWh,    specific CO2 emissions (grid)
             "pv_stc_area": 10000,          # m2,           roof area for pv or stc
             "MIPGap":      0.0001          # ---,          MIP gap
             }

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    devs = {}

    #%% BOILER
    devs["BOI"] = {"inv_var": 52,       # kEUR/MW_th,       variable investment
                   "eta_th": 0.95,      # ---,              thermal efficiency
                   "life_time": 30,     # a,                operation time
                   "cost_om": 0.01,     # ---,              annual operation and maintenance costs as share of investment
                   }

    #%% COMBINED HEAT AND POWER
    devs["CHP"] = {"inv_var": 570,      # kEUR/MW_el,       variable investment
                   "eta_el": 0.35,      # ---,              electrical efficiency
                   "eta_th": 0.5,       # ---,              thermal efficiency
                   "life_time": 30,     # a,                operation time
                   "cost_om": 0.05,     # ---,              annual operation and maintenance costs as share of investment
                   }

    #%% ELECTRICAL HEATER
    devs["EH"] = {"inv_var": 78,        # kEUR/MW_th,       variable investment
                  "eta_th": 0.9,        # ---,              thermal efficiency
                  "life_time": 20,      # a,                operation time
                  "cost_om": 0.01,      # ---,              annual operation and maintenance costs as share of investment
                  }

    #%% AIR SOURCE HEAT PUMP
    devs["ASHP"] = {"inv_var": 260,     # kEUR/MW_th,       variable investment
                     "eta": 0.4,        # ---,              efficiency (COP / COP_rev)
                     "t_supply": 343,   # K,                supply temperature (343 K = 70 degC)
                     "COP_const": 3,    # ---,              COP, if constant COP is assumed
                     "max_cap": 4,      # MW,               maximum heating capacity
                     "min_cap": 0.05,   # MW_th,            minimum heating capacity
                     "life_time": 20,   # a,                operation time
                     "cost_om": 0.03,   # ---,              annual operation and maintenance costs as share of investment
                     }
    
    # Calculate COP from ambient temperature
    devs["ASHP"]["COP"] = calc_COP_AHSP(devs, weather_dict)

    #%% ABSORPTION CHILLER
    devs["AC"] = {"inv_var": 78,        # kEUR/MW_th,       variable investment
                  "eta_th": 0.8,        # ---,              thermal efficiency (cooling power / heating power)
                  "life_time": 20,      # a,                operation time
                  "cost_om": 0.05,      # ---,              annual operation and maintenance costs as share of investment
                  }

    #%% COMPRESSION CHILLER
    devs["CC"] = {"inv_var": 78,        # kEUR/MW_th,       variable investment
                  "COP": 5,             # ---,              coefficient of performance
                  "life_time": 20,      # a,                operation time
                  "cost_om": 0.03,      # ---,              annual operation and maintenance costs as share of investment
                  }

    #%% BATTERY
    devs["BAT"] = {"inv_var": 520,      # kEUR/MWh_el,      variable investment
                   "max_cap": 50,       # MWh_el,           maximum eletrical storage capacity
                   "min_cap": 0.05,     # MWh_el,           minimum eletrical storage capacity
                   "sto_loss": 0,       # 1/h,              standby losses over one time step
                   "eta_ch": 0.9592,    # ---,              charging efficiency
                   "eta_dch": 0.9592,   # ---,              discharging efficiency
                   "max_ch": 25,        # MW,               maximum charging power
                   "max_dch": 25,       # MW,               maximum discharging power
                   "soc_init": 0.8,     # ---,              maximum initial relative state of charge
                   "soc_max": 1,        # ---,              maximum relative state of charge
                   "soc_min": 0,        # ---,              minimum relative state of charge
                   "life_time": 10,     # a,                operation time
                   "cost_om": 0.02,     # ---,              annual operation and maintenance costs as share of investment
                   }

    #%% (HEAT) THERMAL ENERGY STORAGE
    devs["TES"] = {"inv_var": 11.7,     # kEUR/MWh_th,      variable investment
                   "max_cap": 5000,       # MWh_th,           maximum thermal storage capacity
                   "min_cap": 0,        # MWh_th,           minimum thermal storage capacity              
                   "sto_loss": 0.005,   # 1/h,              standby losses over one time step
                   "eta_ch": 0.975,     # ---,              charging efficiency
                   "eta_dch": 0.975,    # ---,              discharging efficiency
                   "max_ch": 1000,      # MW,               maximum charging power
                   "max_dch": 1000,     # MW,               maximum discharging power
                   "soc_init": 0.8,     # ---,              maximum initial state of charge
                   "soc_max": 1,        # ---,              maximum state of charge
                   "soc_min": 0,        # ---,              minimum state of charge
                   "life_time": 20,     # a,                operation time
                   "cost_om": 0.01,     # ---,              annual operation and maintenance costs as share of investment
                   }

    #%% COLD THERMAL ENERGY STORAGE
    devs["CTES"] = {"inv_var": 11.7,    # kEUR/MWh_th,      variable investment
                    "max_cap": 5000,      # MWh_th,           maximum thermal storage capacity
                    "min_cap": 0,       # MWh_th,           minimum thermal storage capacity              
                    "sto_loss": 0.005,  # 1/h,              standby losses over one time step
                    "eta_ch": 0.975,    # ---,              charging efficiency
                    "eta_dch": 0.975,   # ---,              discharging efficiency
                    "max_ch": 1000,     # MW,               maximum charging power
                    "max_dch": 1000,    # MW,               maximum discharging power
                    "soc_init": 0.8,    # ---,              maximum initial state of charge
                    "soc_max": 1,       # ---,              maximum state of charge
                    "soc_min": 0,       # ---,              minimum state of charge
                    "life_time": 20,    # a,                operation time
                    "cost_om": 0.01,    # ---,              annual operation and maintenance costs as share of investment
                    }

    #%% WIND TURBINE
    devs["WT"] = {"inv_var": 650,       # kEUR/MW,        investment per wind turbine
                  "max_cap": 10,        # MW_el,          maximum installed wind power capacity (20 midsized turbines, 500 kW each)
                  "min_cap": 0,         # MW_el,          minimum installed wind power capacity
                  "life_time": 20,      # a,              operation time
                  "cost_om": 0.03,      # ---,            annual operation and maintenance costs as share of investment

                  # parameter for wind speed calculation in hub height
                  "ref_height": 10,     # m,              height of wind speed measurement
                  "expo_a": 0.28,       # ---,            exponent for height correction according to Kleemann und Meliß

                  # wind turbine data
                  "hub_height": 48,     # m,              hub height of wind turbine
                  "rated_power": 500,   # kW
                  }
    
    devs["WT"]["power_curve"] =   {0:  (0.0,    0.00),
                                   1:  (2.4,    0.00),
                                   2:  (2.5,    1.14),
                                   3:  (3.0,    4.37),
                                   4:  (3.5,   10.64),
                                   5:  (4.0,   18.87),
                                   6:  (4.5,   29.77),
                                   7:  (5.0,   40.39),
                                   8:  (5.5,   52.85),
                                   9:  (6.0,   69.36),
                                   10: (6.5,   88.02),
                                   11: (7,    112.19),
                                   12: (7.5,  134.67),
                                   13: (8,    165.38),
                                   14: (8.5,  197.08),
                                   15: (9,    236.89),
                                   16: (9.5,  279.46),
                                   17: (10,   328.00),
                                   18: (10.5, 362.93),
                                   19: (11,   396.64),
                                   20: (11.5, 435.27),
                                   21: (12,   465.15),
                                   22: (12.5, 483.63),
                                   23: (13,   495.95),
                                   24: (14,   500.00),
                                   25: (25,   500.00),
                                   26: (25.1,   0.00),
                                   27: (1000,   0.00),
                                   }
    
    # Calculate power output
    devs["WT"] = calc_wind(devs["WT"], weather_dict)

    #%% PHOTOVOLTAIC
    devs["PV"] = {"inv_var": 909,           # kEUR/MW_el,   variable investment
                  "min_cap": 0,             # MW_el,        minimum electrical capacity
                  "life_time": 20,          # a,            operation time
                  "cost_om": 0.02,          # ---,          annual operation and maintenance costs as share of investment

                  # surface orientation
                  "elevation": 25,          # deg,          surface elevation angle: angle between collector surface and the horizontal
                                            #               0 <= elevation <= 180; if elevation > 90, the surface faces downwards
                  "azimuth": 0,             # deg,          surface azimuth angle: south: 0
                                            #               -180 <= azimuth <= 180; east: negative and west positive

                  # collector data (based on https://www.photovoltaik4all.de/lg-solar-lg360q1c-a5-neon-r)
                  "power_noct": 271,        # W,
                  "temp_amb_noct": 20,      # degC,
                  "solar_noct": 800,        # W/m2,
                  "gamma": 0.003,           # 1/K,
                  "temp_cell_noct": 44,     # degC,
                  "module_area": 1.7272,    # m2,
                  "nom_module_power": 360,  # W,
                  }
    devs["PV"]["power_per_area"] = devs["PV"]["nom_module_power"] / devs["PV"]["module_area"] / 100 # MW/ha
   
    # Calculate pv power
    devs["PV"]["power"] = calc_pv(devs["PV"], weather_dict)

    #%% SOLAR THERMAL COLLECTOR
    devs["STC"] = {"inv_var": 800,          # kEUR/MW_th,   variable investment
                   "life_time": 20,         # a,            operation time
                   "cost_om": 0.01,         # ---,          annual operation and maintenance costs as share of investment

                   # Surface orientation
                   "elevation": 30,         # deg,          surface elevation angle: angle between collector surface and the horizontal
                                            #               0 <= elevation <= 180; if elevation > 90, the surface faces downwards
                   "azimuth": 0,            # deg,          surface azimuth angle: south: 0
                                            #               -180 <= azimuth <= 180; east: negative and west positive

                   # Collector data (based on "HTHEATboost 35/10" by Arcon-Sunmark A/S)
                   "eta_0": 0.779,          # ---,         optical efficiency
                   "a1": 2.41,              # W/(m2 K),    linear loss coefficient
                   "a2": 0.015,             # W/(m2 K2),   quadratic loss coefficient
                   "temp_mean":  (95+85)/2, # degC,        mean fluid temperature
                   "power_per_m2": 777      # W/m2,        power output per m2 collector area at temp_mean - temp_amb = 0
                   }

    devs["STC"]["power_per_area"] = devs["STC"]["power_per_m2"] / 100 # MW/ha

    # Calculate thermal output of solar thermal colletors
    devs["STC"]["heat"] = calc_stc(devs, weather_dict)

    # Calculate annualized investment of every device
    devs = calc_annual_investment(devs, param)   
    return (devs, param, dem)

#%%
def get_irrad_profile(ele, azim, weather_dict):
    """
    Calculates global irradiance on tilted surface from weather file.
    """

    # Load time series as numpy array
    dtype = dict(names = ['id','data'], formats = ['f8','f8'])
    sun_diffuse = np.array(list(weather_dict["Diffuse Horizontal Radiation"].items()), dtype=dtype)['data']
    sun_global = np.array(list(weather_dict["Global Horizontal Radiation"].items()), dtype=dtype)['data']
    sun_direct = sun_global - sun_diffuse

    # Define local properties
    time_zone = 7                # ---,      time zone (weather file works properly with time_zone = 7, although time_zone = 8 is proposed in the weather file)
    location = (31.17, 121.43)   # degree,   latitude, longitude of location
    altitude = 7.0               # m,        height of location above sea level

    # Calculate geometric relations
    geometry = sun.getGeometry(0, 3600, 8760, time_zone, location, altitude)
    (omega, delta, thetaZ, airmass, Gon) = geometry
    theta = sun.getIncidenceAngle(ele, azim, location[0], omega, delta)

    theta = theta[1] # cosTheta is not required

    # Calculate radiation on tilted surface
    return sun.getTotalRadiationTiltedSurface(theta, thetaZ, sun_direct, sun_diffuse, airmass, Gon, ele, 0.2)

#%%
def calc_pv(dev, weather_dict):
    """
    Calculates photovoltaic output in MW per MW_peak.
    Model based on http://www.sciencedirect.com/science/article/pii/S1876610213000829, equation 5.

    """

    # Calculate global tilted irradiance in W/m2
    gti_pv = get_irrad_profile(dev["elevation"], dev["azimuth"], weather_dict)

    # Get ambient temperature from weather dict
    temp_amb = np.array(list(weather_dict["Dry Bulb Temperature"].items()), dtype=dict(names = ['id','data'], formats = ['f8','f8']))['data']

    temp_cell = temp_amb + gti_pv / dev["solar_noct"] * (dev["temp_cell_noct"] - temp_amb)
    eta_noct = dev["power_noct"] / (dev["module_area"] * dev["solar_noct"])
    eta_cell = eta_noct * (1 - dev["gamma"] * (temp_cell - dev["temp_amb_noct"]))

    # Calculate collector area (m2) per installed capacity (MW_peak)
    area_per_MW_peak = dev["module_area"] / (dev["nom_module_power"] / 1000000)

    # Calculate power generation in MW/MW_peak
    pv_output = eta_cell * (gti_pv / 1000000) * area_per_MW_peak

    return dict(enumerate(pv_output))

#%%
def calc_stc(devs, weather_dict):
    """
    Calculation of thermal output in MW/MW_peak according to ISO 9806 standard (p. 43).

    """

    dev = devs["STC"]

    # Calculate global tilted irradiance in W/m2
    gti_stc = get_irrad_profile(dev["elevation"], dev["azimuth"], weather_dict)

    # Get ambient temperature from weather dict
    temp_amb = np.array(list(weather_dict["Dry Bulb Temperature"].items()), dtype=dict(names = ['id','data'], formats = ['f8','f8']))['data']

    # Calculate heat output in W/m2
    stc_output_m2 = np.zeros(gti_stc.size)
    t_norm = (dev["temp_mean"] - temp_amb) / gti_stc
    eta_th = dev["eta_0"] - dev["a1"] * t_norm - dev["a2"] * t_norm**2 #* gti_stc
    for t in range(eta_th.size):
        if not np.isfinite(eta_th[t]):
            eta_th[t] = 0
        stc_output_m2[t] = max(eta_th[t] * gti_stc[t], 0)

    # Calculate collector area (m2) per installed capacity (MW_peak)
    area_per_MW_peak = 1000000 / dev["power_per_m2"]

    # Calculate thermal heat output in MW/MW_peak
    stc_output = stc_output_m2 * area_per_MW_peak / 1000000

    return dict(enumerate(stc_output))

#%%
def calc_wind(dev, weather_dict):
    """
    Calculation power output from wind turbines in MW/MW_peak.
    
    """
    
    power_curve = dev["power_curve"]
    
    dev["power"] = {}
    for t in range(len(weather_dict["Wind Speed"])):
        wind_speed_ground = weather_dict["Wind Speed"][t]
        wind_speed_shaft = wind_speed_ground * (dev["hub_height"] / dev["ref_height"]) ** dev["expo_a"]
        if wind_speed_shaft <= 0:
            dev["power"][t] = 0
        elif wind_speed_shaft > power_curve[len(power_curve)-1][0]:
            print("Warning: Wind speed is " + str(wind_speed_shaft) + " m/s and exceeds wind power curve table.")
            dev["power"][t] = 0
    
        # Linear interpolation
        else:
            for k in range(len(power_curve)):
                if power_curve[k][0] > wind_speed_shaft:
                    dev["power"][t] = (power_curve[k][1]-power_curve[k-1][1])/(power_curve[k][0]-power_curve[k-1][0]) * (wind_speed_shaft-power_curve[k-1][0]) + power_curve[k-1][1]
                    break
            
    return dev

#%%
def calc_COP_AHSP(devs, weather_dict):
    """
    Calculation of COP for air source heat pump based on carnot efficiency.

    """

    devs["ASHP"]["COP"] = {}
    for t in weather_dict["Dry Bulb Temperature"].keys():
        air_temp = weather_dict["Dry Bulb Temperature"][t]
        devs["ASHP"]["COP"][t] = devs["ASHP"]["eta"] * (devs["ASHP"]["t_supply"]/(devs["ASHP"]["t_supply"]-(air_temp + 273)))
    return devs["ASHP"]["COP"]

#%%
def calc_annual_investment(devs, param):
    """
    Calculation of total investment costs including replacements (based on VDI 2067-1, pages 16-17).
    
    Annualized fix and variable investment is returned.
    
    """

    observation_time = param["observation_time"]
    interest_rate = param["interest_rate"]
    q = 1 + param["interest_rate"]

    # Calculate capital recovery factor
    CRF = ((q**observation_time)*interest_rate)/((q**observation_time)-1)

    for device in devs.keys():

        # If there are no fix costs:
        devs[device]["inv_fix"] = 0
        
        life_time = devs[device]["life_time"]
        inv_fix_init = devs[device]["inv_fix"]
        inv_var_init = devs[device]["inv_var"]
        inv_fix_repl = devs[device]["inv_fix"]
        inv_var_repl = devs[device]["inv_var"]

        # Number of required replacements
        n = int(math.floor(observation_time / life_time))

        # Inestment for replcaments
        invest_replacements = sum((q ** (-i * life_time)) for i in range(1, n+1))

        # Residual value of final replacement
        res_value = ((n+1) * life_time - observation_time) / life_time * (q ** (-observation_time))

        # Calculate annualized investments       
        if life_time > observation_time:
            devs[device]["ann_inv_fix"] = (inv_fix_init * (1 - res_value)) * CRF 
            devs[device]["ann_inv_var"] = (inv_var_init * (1 - res_value)) * CRF 
        else:
            devs[device]["ann_inv_fix"] = (inv_fix_init + inv_fix_repl * (invest_replacements - res_value)) * CRF
            devs[device]["ann_inv_var"] = (inv_var_init + inv_var_repl * (invest_replacements - res_value)) * CRF 

    return devs