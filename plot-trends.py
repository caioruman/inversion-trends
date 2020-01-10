import numpy as np
import pandas as pd
import sys
import os
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt

from glob import glob
#from rpn.rpn import RPN
#from rpn.domains.rotated_lat_lon import RotatedLatLon
#from rpn import level_kinds

from netCDF4 import Dataset
import time

'''
    Plot trends, reading from the CSV files
'''

def main():

  # 1st: Read the file with the inversion strength and frequency
# /pixel/project01/cruman/ModelData/inversionv2/PanArctic_0.5d_CanRCP45_NOCTEM_R2/InversionV2/Inversion_925_1000_ERA_205804.nc
  folder_loc = "/pixel/project01/cruman/ModelData/inversionv2/"

  exps = ['PanArctic_0.5d_CanHisto_NOCTEM_RUN', 'PanArctic_0.5d_CanHisto_NOCTEM_R2', 'PanArctic_0.5d_CanHisto_NOCTEM_R3',
          'PanArctic_0.5d_CanHisto_NOCTEM_R4', 'PanArctic_0.5d_CanHisto_NOCTEM_R5',  'PanArctic_0.5d_CanRCP45_NOCTEM_R2', 
          'PanArctic_0.5d_CanRCP45_NOCTEM_R3', 'PanArctic_0.5d_CanRCP45_NOCTEM_R5', 'PanArctic_0.5d_CanRCP45_NOCTEM_R4', 
          'PanArctic_0.5d_CanRCP45_NOCTEM_RUN']

  datai = 1976
  dataf = 2099

  years = range(datai, dataf+1)
  

  periods = [[12, 1, 2], [6, 7, 8]]
  p_name = ["DJF", "JJA"]

  #master_list_dt = []   # Even elements: DJF; Odd elements: JJA
  #master_list_freq = []
  master_list_dt = np.zeros([21, 4, len(years), len(p_name)])
  master_list_freq = np.zeros([21, 4, len(years), len(p_name)])

  for i, year in enumerate(years):
    if (year%10==0):
      print(year)

    df = pd.read_csv('CSV/TimeSeries_Inv_RCP85_{0}.csv'.format(year), skipinitialspace=True, index_col=0)        

    for j, period in enumerate(periods):    
      
      # 0, 1: mean and std for 85
      # 2, 3: mean and std for 45

      for region in range(1, 22):        

        aux_dt, aux_dt_std, aux_freq , aux_freq_std = read_inv(df, 'CanHisto', region, period)

        master_list_dt[region-1, 0, i, j] = aux_dt
        master_list_dt[region-1, 1, i, j] = aux_dt_std

        master_list_freq[region-1, 0, i, j] = (1-aux_freq)
        master_list_freq[region-1, 1, i, j] = aux_freq_std

        aux_dt, aux_dt_std, aux_freq , aux_freq_std = read_inv(df, 'CanRCP45', region, period)

        master_list_dt[region-1, 2, i, j] = aux_dt
        master_list_dt[region-1, 3, i, j] = aux_dt_std

        master_list_freq[region-1, 2, i, j] = (1-aux_freq)
        master_list_freq[region-1, 3, i, j] = aux_freq_std
          
  #print(master_list_freq[0, 1, :, 0])

  
  for reg in range(0,21):
    #dt_85 = master_list_dt[reg, 0, :]
    #dt_85_std = master_list_dt[reg, 1, :]

    #dt_45 = master_list_dt[reg, 2, :]
    #dt_45_std = master_list_dt[reg, 3, :]    

  # Winter[region, value, year, period], Summer
    plot_trends(master_list_dt[reg, :, :, 0], master_list_dt[reg, :, :, 1], years, 'dt_{0}'.format(reg+1), 'Inversion Strength (K)', reg)

    plot_trends(master_list_freq[reg, :, :, 0]*100, master_list_freq[reg, :, :, 1]*100, years, 'freq_{0}'.format(reg+1), 'Inversion Frequency (%)', reg, 10)
   
  # Plot stuff
  # 21 plots, one for each region. Each plot is a time series of RCP45 and RCP85 in each. Summer and Winter.

def plot_trends(data_w, data_s, data_x, region, label_y, reg, val=1):

  value_w_85 = data_w[0, :]
  std_w_85 = data_w[1, :]

  value_w_45 = data_w[2, :]
  std_w_45 = data_w[3, :]

  fig, ax = plt.subplots(1,1,figsize=(16, 5), dpi= 80) 

  plt.plot(data_x, value_w_85, 'o-', lw=1.5, color='darkblue', label='RCP85 - Winter')  
  plt.plot(data_x, value_w_45, 'o-', lw=1.5, color='dodgerblue', label='RCP45 - Winter')

  #plt.errorbar(data_x, value_w_85, yerr=std_w_85, fmt='o-', lw=1.5, color='darkblue', label='RCP85 - Winter')  
  #plt.errorbar(data_x, value_w_45, yerr=std_w_45, fmt='o-', lw=1.5, color='dodgerblue', label='RCP45 - Winter')  

  # Trendline
  z = np.polyfit(data_x, value_w_85, 1)
  p = np.poly1d(z)
  plt.plot(data_x,p(data_x),"--", color='darkblue')

  z = np.polyfit(data_x, value_w_45, 1)
  p = np.poly1d(z)
  plt.plot(data_x,p(data_x),"--", color='dodgerblue')

  value_w_85 = data_s[0, :]
  std_w_85 = data_s[1, :]

  value_w_45 = data_s[2, :]
  std_w_45 = data_s[3, :] 

  plt.plot(data_x, value_w_85, 'o-', lw=1.5, color='firebrick', label='RCP85 - Summer')  
  plt.plot(data_x, value_w_45, 'o-', lw=1.5, color='orangered', label='RCP45 - Summer')  

  #plt.errorbar(data_x, value_w_85, yerr=std_w_85, fmt='o-', lw=1.5, color='firebrick', label='RCP85 - Summer')  
  #plt.errorbar(data_x, value_w_45, yerr=std_w_45, fmt='o-', lw=1.5, color='orangered', label='RCP45 - Summer')  

  # Trendline
  z = np.polyfit(data_x, value_w_85, 1)
  p = np.poly1d(z)
  plt.plot(data_x,p(data_x),"--", color='firebrick')

  z = np.polyfit(data_x, value_w_45, 1)
  p = np.poly1d(z)
  plt.plot(data_x,p(data_x),"--", color='orangered')

  # Draw Tick lines  
  for y in range(1*val, 10*val+1, 1*val):    
    plt.hlines(y, xmin=data_x[0], xmax=data_x[-1], colors='black', alpha=0.3, linestyles="--", lw=0.5)

  # Lighten borders
  plt.gca().spines["top"].set_alpha(.3)
  plt.gca().spines["bottom"].set_alpha(.3)
  plt.gca().spines["right"].set_alpha(.3)
  plt.gca().spines["left"].set_alpha(.3)
  
  reg_name = return_regname(reg+1)
  plt.title('Region {0} - {1}'.format(reg+1, reg_name), fontsize=22)
  plt.yticks(range(1*val, 10*val+1, 1*val), [str(y) for y in range(1*val, 10*val+1, 1*val)], fontsize=24)    
  plt.xticks(range(1970, 2101, 10), fontsize=24)
  plt.ylim(0, 10*val+1)    
  plt.xlim(data_x[0]-1, data_x[-1]+1)  
  plt.legend()
  plt.ylabel(label_y, fontsize=20)  

  plt.savefig('figure_{0}.png'.format(region))
  plt.close()
  

def return_regname(reg):

  if (reg == 1):
    name = 'Greenland'
  elif (reg == 2):
    name = 'Chukchi Sea'
  elif (reg == 3):
    name = 'Canada Basin'
  elif (reg == 4):
    name = 'Central Arctic'
  elif (reg == 5):
    name = 'Laptev Sea'
  elif (reg == 6):
    name = 'North Pole'
  elif (reg == 7):
    name = 'Nansen Basin'
  elif (reg == 8):
    name = 'Barents Sea'
  elif (reg == 9):
    name = 'Greenland/Norwengian Seas'
  elif (reg == 10):
    name = 'Baffin Bay'
  elif (reg == 11):
    name = 'Arctic Canada Archipelago'
  elif (reg == 12):
    name = 'Hudson Bay'
  elif (reg == 13):
    name = 'North Europe'
  elif (reg == 14):
    name = 'NC Russia'
  elif (reg == 15):
    name = 'NE Russia'
  elif (reg == 16):
    name = 'Alaska'
  elif (reg == 17):
    name = 'NWT and Yukon'
  elif (reg == 18):
    name = 'Beaufort Sea'
  elif (reg == 19):
    name = 'Baffin Island'
  elif (reg == 20):
    name = 'Continental Nunavut'
  elif (reg == 21):
    name = 'Kara Sea'
  else:
    name = 'No Match'

  return name


def read_inv(df, simName, region, period):

  df_ = df.loc[(df['SimName'].str.contains(simName)==True) & (df['Region'] == region) & (df['Month'].isin(period))]

  return df_['DT'].mean(), df_['DT'].std(), df_['FREQ'].mean(), df_['FREQ'].std()

if __name__ == "__main__":
    main()
