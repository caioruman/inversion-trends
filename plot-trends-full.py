import numpy as np
import pandas as pd
import sys
import os
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from os import listdir

from glob import glob

from netCDF4 import Dataset
import time

'''
  Plot trends, reading from the CSV files
  Now using subplots
'''

def main():

  folder_loc = "/pixel/project01/cruman/ModelData/inversionv2/"

  exps = ['PanArctic_0.5d_CanHisto_NOCTEM_RUN', 'PanArctic_0.5d_CanHisto_NOCTEM_R2', 'PanArctic_0.5d_CanHisto_NOCTEM_R3',
          'PanArctic_0.5d_CanHisto_NOCTEM_R4', 'PanArctic_0.5d_CanHisto_NOCTEM_R5',  'PanArctic_0.5d_CanRCP45_NOCTEM_R2', 
          'PanArctic_0.5d_CanRCP45_NOCTEM_R3', 'PanArctic_0.5d_CanRCP45_NOCTEM_R5', 'PanArctic_0.5d_CanRCP45_NOCTEM_R4', 
          'PanArctic_0.5d_CanRCP45_NOCTEM_RUN']

  datai = 1979
  dataf = 2099

  years = range(datai, dataf+1)

  vars = [('DT', 'Inversion Strength ($^\circ$C)'), ('FREQ', 'Inversion Frequency (%)'), 
          ('T2M_J8', '2m Temperature ($^\circ$C)'), ('CloudCover', 'Cloud Cover (%)'),
          ('ATM_H20', 'Total Precipitable\n Water (mm)'), ('SeaIce', 'Sea Ice (%)'),
          ('SH', 'Sensible Heat\n Flux (Wm$^-$$^2$)'), ('LH', 'Latent Heat\n Flux (Wm$^-$$^2$)')]

  periods = [[12, 1, 2], [6, 7, 8]]
  regions = [[6, 7, 3, 4, 22], [18, 2, 5], [21], [8], [10, 12], [11], [16], [17], [19, 20], [13, 14], [15], [1], [9]]
  p_name = ["DJF", "JJA"]

  #master_list_dt = np.zeros([21, 4, len(years), len(p_name)])
  master_list_dt = np.zeros([21, 4, len(years), len(p_name)])
  master_list_freq = np.zeros([21, 4, len(years), len(p_name)])
  master_list_sh = np.zeros([21, 4, len(years), len(p_name)])
  master_list_lh = np.zeros([21, 4, len(years), len(p_name)])
  ml_t2m = np.zeros([21, 4, len(years), len(p_name)])
  ml_cc = np.zeros([21, 4, len(years), len(p_name)])
  ml_h2o = np.zeros([21, 4, len(years), len(p_name)])
  ml_seaice = np.zeros([21, 4, len(years), len(p_name)])

  # get the values for DT and Freq
  master_list_dt, master_list_freq = getDataInversion(master_list_dt, master_list_freq, years, periods, regions)

  # get the values for the fluxes
  master_list_sh, master_list_lh = getDataFluxes(master_list_sh, master_list_lh, years, periods, regions)

  # get the values for the other variables
  ml_t2m, ml_cc, ml_h2o, ml_seaice = getData(ml_t2m, ml_cc, ml_h2o, ml_seaice, years, periods, regions)

  file1 = open("data_trends_RCP8.5.txt","w")
  file1.write("Region, Variable, Season, RCP, LastValue, InitialValue\n")

  file2 = open("data_trends_rcp4.5.txt", "w")
  file2.write("Region, Variable, Season, RCP, LastValue, InitialValue\n")

  # loop the regions
  for rr, region in enumerate(regions):
  # start the fig element and subplots here
    fig, axs = plt.subplots(4, 2, figsize=(20,12), sharex=True)
    fig.subplots_adjust(hspace=0.06, wspace=0.15)

    # ax1 and ax2: dt freq and dt inv
    for ax, vv in zip(axs.flat, vars):
      
      step, ymax, ymin = getSteps(vv[0])

      if (vv[0] == 'CloudCover'):
        data_w = ml_cc[rr, :, :, 0]
        data_s = ml_cc[rr, :, :, 1]
      elif (vv[0] == 'SeaIce'):
        data_w = ml_seaice[rr, :, :, 0]
        data_s = ml_seaice[rr, :, :, 1]
      elif (vv[0] == 'T2M_J8'):
        data_w = ml_t2m[rr, :, :, 0]
        data_s = ml_t2m[rr, :, :, 1]
      elif (vv[0] == "SH"):
        data_w = master_list_sh[rr, :, :, 0]
        data_s = master_list_sh[rr, :, :, 1]
      elif (vv[0] == "LH"):
        data_w = master_list_lh[rr, :, :, 0]
        data_s = master_list_lh[rr, :, :, 1]
      elif (vv[0] == "ATM_H20"):
        data_w = ml_h2o[rr, :, :, 0]
        data_s = ml_h2o[rr, :, :, 1]
      elif (vv[0] == "DT"):
        data_w = master_list_dt[rr, :, :, 0]
        data_s = master_list_dt[rr, :, :, 1]
      elif (vv[0] == "FREQ"):
        data_w = master_list_freq[rr, :, :, 0]
        data_s = master_list_freq[rr, :, :, 1]

      print(region, vv[0], 'Winter', 'RCP85', data_w[0,-1], data_w[0,0])
      print(region, vv[0], 'Winter', 'RCP45', data_w[2,-1], data_w[2,0])

      print(region, vv[0], 'Summer', 'RCP85', data_s[0,-1], data_s[0,0])
      print(region, vv[0], 'Summer', 'RCP45', data_s[2,-1], data_s[2,0])

      file1.write("{0}, {1}, {2}, {3}, {4:2.3f}, {5:2.3f}\n".format(region, vv[0], 'Winter', 'RCP85', data_w[0,-1], data_w[0,0]))
      file2.write("{0}, {1}, {2}, {3}, {4:2.3f}, {5:2.3f}\n".format(region, vv[0], 'Winter', 'RCP45', data_w[2,-1], data_w[2,0]))
      file1.write("{0}, {1}, {2}, {3}, {4:2.3f}, {5:2.3f}\n".format(region, vv[0], 'Summer', 'RCP85', data_s[0,-1], data_s[0,0]))
      file2.write("{0}, {1}, {2}, {3}, {4:2.3f}, {5:2.3f}\n".format(region, vv[0], 'Summer', 'RCP45', data_s[2,-1], data_s[2,0]))

      ax = plot_trends(ax, data_w, data_s, years, step, ymax, ymin)

      ax.set_xticks(range(1970, 2101, 10))
      ax.set_yticks(range(ymin+step, ymax, step))
      ax.xaxis.set_tick_params(labelsize=18, rotation=45)
      ax.yaxis.set_tick_params(labelsize=16)
      ax.set_xlim(1979, 2100)  
      ax.set_ylabel(vv[1], fontsize=14)

      if vv[0] == "DT":
        ax.legend()

      # Lighten borders
      ax.spines["top"].set_alpha(.3)
      ax.spines["bottom"].set_alpha(.3)
      ax.spines["right"].set_alpha(.3)
      ax.spines["left"].set_alpha(.3)

    reg_name = return_regname(rr+1)
    plt.suptitle('Region {0} - {1}'.format(rr+1, reg_name), fontsize=22, y=0.93)
    plt.savefig('plot_region_{0}.png'.format(rr+1))
  file1.close()

def getSteps(var):

  if (var == 'CloudCover') or (var == 'SeaIce'):
    ymin = 0
    ymax = 100
    step = 10
  elif (var == 'T2M_J8'):
    ymin = -35
    ymax = 21
    step = 5
  elif (var == 'Wind'):
    ymin = 0
    ymax = 10
    step = 1
  elif (var == "LW_down"):
    ymin = 100
    ymax = 360
    step = 40
  elif (var == "SH"):
    #if (region[0] == 21):    
    #  ymin = -30
    #  ymax = 30
    #  step = 10    
    #elif (region[0] == 8) or (region[0] == 16):
    #  ymin = -10
    #  ymax = 80
    #  step = 10    
    #else:
    ymin = -20
    ymax = 80
    step = 10    
    #print(ymin, ymax, step)
  elif (var == "ATM_H20"):
    ymin = -5
    ymax = 40
    step = 5
  elif (var == "DT"):
    ymin = 0
    ymax = 10
    step = 1
  elif (var == "FREQ"):
    ymin = 0
    ymax = 100
    step = 10
  else:
    ymin = -10
    ymax = 80
    step = 10


  return step, ymax, ymin

def plot_trends(ax, data_w, data_s, data_x, step, ymax, ymin):

  value_w_85 = data_w[0, :]
  std_w_85 = data_w[1, :]

  value_w_45 = data_w[2, :]
  std_w_45 = data_w[3, :]

  ax.plot(data_x, value_w_85, '-', lw=1.5, color='darkblue', label='RCP85 - Winter') 

  ax.fill_between(data_x, value_w_85-std_w_85, value_w_85+std_w_85, alpha=0.25, edgecolor='darkblue', facecolor='darkblue')

  ax.plot(data_x, value_w_45, '-', lw=1.5, color='dodgerblue', label='RCP45 - Winter')

  ax.fill_between(data_x, value_w_45-std_w_45, value_w_45+std_w_45, alpha=0.25, edgecolor='dodgerblue', facecolor='dodgerblue')  

  #plt.errorbar(data_x, value_w_85, yerr=std_w_85, fmt='o-', lw=1.5, color='darkblue', label='RCP85 - Winter')  
  #plt.errorbar(data_x, value_w_45, yerr=std_w_45, fmt='o-', lw=1.5, color='dodgerblue', label='RCP45 - Winter')  

  value_w_85 = data_s[0, :]
  std_w_85 = data_s[1, :]

  value_w_45 = data_s[2, :]
  std_w_45 = data_s[3, :] 

  ax.plot(data_x, value_w_85, '-', lw=1.5, color='firebrick', label='RCP85 - Summer')  

  ax.fill_between(data_x, value_w_85-std_w_85, value_w_85+std_w_85, alpha=0.25, edgecolor='firebrick', facecolor='firebrick')

  ax.plot(data_x, value_w_45, '-', lw=1.5, color='orangered', label='RCP45 - Summer')  

  ax.fill_between(data_x, value_w_45-std_w_45, value_w_45+std_w_45, alpha=0.25, edgecolor='orangered', facecolor='orangered')

  #plt.errorbar(data_x, value_w_85, yerr=std_w_85, fmt='o-', lw=1.5, color='firebrick', label='RCP85 - Summer')  
  #plt.errorbar(data_x, value_w_45, yerr=std_w_45, fmt='o-', lw=1.5, color='orangered', label='RCP45 - Summer')  

  # Draw Tick lines  
  for y in range(ymin, ymax, step):    
  #for y in range(1*val, 10*val+1, 1*val):  
    ax.hlines(y, xmin=data_x[0], xmax=data_x[-1], colors='black', alpha=0.3, linestyles="--", lw=0.5)

  #ax.set_yticks(range(ymin, ymax, step), [str(y) for y in range(ymin, ymax, step)])    
  ax.set_ylim(ymin, ymax)

  

  return ax

def getData(ml_t2m, ml_cc, ml_h2o, ml_seaice, years, periods, regions):

  for i, year in enumerate(years):
    if (year%10==0):
      print(year)

    li = []
    #TimeSeries_Inv_RCP85_1981.csv
    # Moving average
    for y in np.arange(year-4,year+4,1):
      try:
        df = pd.read_csv('CSV/TimeSeries_Vars_{0}.csv'.format(year), skipinitialspace=True, index_col=0)   
        #df = pd.read_csv('CSV/TimeSeries_Flux_{0}.csv'.format(year), skipinitialspace=True, index_col=0)      
        li.append(df)
      except:
        print("no file with the year {0}".format(y))
    

    df = pd.concat(li, axis=0, ignore_index=True)
    #df['FREQ'] = 1 - df['FREQ']  

    for j, period in enumerate(periods):    
      
      # 0, 1: mean and std for 85
      # 2, 3: mean and std for 45        

      for rr, region in enumerate(regions):

        aux, aux_std = read_inv(df, 'CanHisto', region, period, 'T2M_J8')

        ml_t2m[rr, 0, i, j] = aux
        ml_t2m[rr, 1, i, j] = aux_std

        aux, aux_std = read_inv(df, 'CanRCP45', region, period, 'T2M_J8')

        ml_t2m[rr, 2, i, j] = aux
        ml_t2m[rr, 3, i, j] = aux_std  

        aux, aux_std = read_inv(df, 'CanHisto', region, period, 'CloudCover')

        ml_cc[rr, 0, i, j] = aux
        ml_cc[rr, 1, i, j] = aux_std    

        aux, aux_std = read_inv(df, 'CanRCP45', region, period, 'CloudCover')        

        ml_cc[rr, 2, i, j] = aux
        ml_cc[rr, 3, i, j] = aux_std   

        aux, aux_std = read_inv(df, 'CanHisto', region, period, 'ATM_H20')

        ml_h2o[rr, 0, i, j] = aux
        ml_h2o[rr, 1, i, j] = aux_std    

        aux, aux_std = read_inv(df, 'CanRCP45', region, period, 'ATM_H20')        

        ml_h2o[rr, 2, i, j] = aux
        ml_h2o[rr, 3, i, j] = aux_std 

        aux, aux_std = read_inv(df, 'CanHisto', region, period, 'SeaIce')

        ml_seaice[rr, 0, i, j] = aux
        ml_seaice[rr, 1, i, j] = aux_std    

        aux, aux_std = read_inv(df, 'CanRCP45', region, period, 'SeaIce')        

        ml_seaice[rr, 2, i, j] = aux
        ml_seaice[rr, 3, i, j] = aux_std 

  return ml_t2m, ml_cc, ml_h2o, ml_seaice

def getDataFluxes(master_list_sh, master_list_lh, years, periods, regions):

  for i, year in enumerate(years):
    if (year%10==0):
      print(year)

    li = []
    #TimeSeries_Inv_RCP85_1981.csv
    # Moving average
    for y in np.arange(year-4,year+4,1):
      try:
        #df = pd.read_csv('CSV/TimeSeries_Vars_{0}.csv'.format(year), skipinitialspace=True, index_col=0)   
        df = pd.read_csv('CSV/TimeSeries_Flux_{0}.csv'.format(year), skipinitialspace=True, index_col=0)      
        li.append(df)
      except:
        print("no file with the year {0}".format(y))
    

    df = pd.concat(li, axis=0, ignore_index=True)
    #df['FREQ'] = 1 - df['FREQ']  

    for j, period in enumerate(periods):    
      
      # 0, 1: mean and std for 85
      # 2, 3: mean and std for 45        

      for rr, region in enumerate(regions):

        aux, aux_std = read_inv(df, 'CanHisto', region, period, 'SH')

        master_list_sh[rr, 0, i, j] = aux
        master_list_sh[rr, 1, i, j] = aux_std

        aux, aux_std = read_inv(df, 'CanHisto', region, period, 'LH')

        master_list_lh[rr, 0, i, j] = aux
        master_list_lh[rr, 1, i, j] = aux_std    

        aux, aux_std = read_inv(df, 'CanRCP45', region, period, 'SH')

        master_list_sh[rr, 2, i, j] = aux
        master_list_sh[rr, 3, i, j] = aux_std  

        aux, aux_std = read_inv(df, 'CanRCP45', region, period, 'LH')        

        master_list_lh[rr, 2, i, j] = aux
        master_list_lh[rr, 3, i, j] = aux_std   

  return master_list_sh, master_list_lh

def getDataInversion(master_list_dt, master_list_freq, years, periods, regions):

  for i, year in enumerate(years):
    if (year%10==0):
      print(year)

    li = []
    #TimeSeries_Inv_RCP85_1981.csv
    # Moving average
    for y in np.arange(year-1,year+2,1):
      try:
        df = pd.read_csv('CSV/TimeSeries_Inv_RCP85_{0}.csv'.format(y), skipinitialspace=True, index_col=0)   
        #print('CSV/TimeSeries_Inv_RCP85_{0}.csv'.format(y))
        li.append(df)
      except:
        print("no file with the year {0}".format(y))
    #df = pd.read_csv('CSV/TimeSeries_Flux_{0}.csv'.format(year), skipinitialspace=True, index_col=0)      

    df = pd.concat(li, axis=0, ignore_index=True)
    df['FREQ'] = (1 - df['FREQ'])*100
    
    for j, period in enumerate(periods):    
      
      # 0, 1: mean and std for 85
      # 2, 3: mean and std for 45

      #for region in range(1, 22):  
      for rr, region in enumerate(regions):    

        aux_dt, aux_dt_std, aux_freq, aux_freq_std = read_inv_dt(df, 'CanHisto', region, period)

        master_list_dt[rr, 0, i, j] = aux_dt
        master_list_dt[rr, 1, i, j] = aux_dt_std

        master_list_freq[rr, 0, i, j] = aux_freq
        master_list_freq[rr, 1, i, j] = aux_freq_std

        #print("RCP85")
        #print(aux_dt)
        #print(aux_freq)

        aux_dt, aux_dt_std, aux_freq, aux_freq_std = read_inv_dt(df, 'CanRCP45', region, period)

        master_list_dt[rr, 2, i, j] = aux_dt
        master_list_dt[rr, 3, i, j] = aux_dt_std

        master_list_freq[rr, 2, i, j] = aux_freq
        master_list_freq[rr, 3, i, j] = aux_freq_std

        #print("RCP45")
        #print(aux_dt)
        #print(aux_freq)

        #sys.exit()
  return master_list_dt, master_list_freq

def return_regname(reg):
  
  #regions = [[6, 7, 3, 4, 22], [18, 2, 5], [21], [8], [10, 12], [11], [16], [17], [19, 20], [13, 14], [15], [1], [9]]
  if (reg == 1):
    name = 'Central Arctic'
  elif (reg == 2):
    name = 'Arctic Ocean north of Pacific'
  elif (reg == 3):
    name = 'Arctic Ocean North of Siberia'
  elif (reg == 4):
    name = 'Arctic Ocean North of Norway'
  elif (reg == 5):
    name = 'Baffin Bay and Hudson Bay'
  elif (reg == 6):
    name = 'Arctic Canada Archipelago'
  elif (reg == 7):
    name = 'Alaska'
  elif (reg == 8):
    name = 'NWT and Yukon'
  elif (reg == 9):
    name = 'Nunavut'
  elif (reg == 10):
    name = 'North Europe and NC Russia'
  elif (reg == 11):
    name = 'NE Russia'
  elif (reg == 12):
    name = 'Greenland'
  elif (reg == 13):
    name = 'Greenland/Norwengian Seas'  
  else:
    name = 'No Match'

  return name

def read_inv_dt(df, simName, region, period):

  df_ = df.loc[(df['SimName'].str.contains(simName)==True) & (df['Region'].isin(region)) & (df['Month'].isin(period))]
  #print(df_.head())
  #print(simName, region, period)

  return df_['DT'].mean(), df_['DT'].std(), df_['FREQ'].mean(), df_['FREQ'].std()

def read_inv(df, simName, region, period, var):

  df_ = df.loc[(df['SimName'].str.contains(simName)==True) & (df['Region'].isin(region)) & (df['Month'].isin(period))]

#  vars = [('CloudCover', 'Cloud Cover (%)'),('SeaIce', 'Sea Ice (%)'), ('ATM_H20', 'Atmosphere Water Content'), 
#          ('T2M_J8', '2m Temperature (C)'), ('Wind', '10m Wind (m/s)')]
#  vars = [('LW_down', 'Downward LW (Wm-2)'),('SH', 'Sensible Heat Flux (Wm-2)'), ('LH', 'Latent Heat Flux (Wm-2)'), 
#          ('LH_net', 'Net LW (Wm-2)')]

  if (var == 'CloudCover') or (var == 'SeaIce'):
    val = df_[var].mean()*100
    val_std = df_[var].std()*100
    ymin = 0
    ymax = 100
    step = 10
  elif (var == 'T2M_J8'):
    aux = df_[var]-273.15
    val = aux.mean()
    val_std = aux.std()
    ymin = 236
    ymax = 294
    step = 4
  elif (var == 'Wind'):
    val = df_[var].mean()/1.944
    val_std = df_[var].std()/1.944
    ymin = 0
    ymax = 10
    step = 1
  elif (var == "LW_down"):
    val = df_[var].mean()*3600
    val_std = df_[var].std()*3600
    ymin = 100
    ymax = 360
    step = 40
  elif (var == "SH"):
    val = df_[var].mean()
    val_std = df_[var].std()
    #print(region[0])
    if (region[0] == 21):    
      ymin = -30
      ymax = 30
      step = 10    
    elif (region[0] == 8) or (region[0] == 16):
      ymin = -10
      ymax = 80
      step = 10    
    else:
      ymin = -10
      ymax = 40
      step = 5    
    #print(ymin, ymax, step)
  elif (var == "ATM_H20"):
    val = df_[var].mean()
    val_std = df_[var].std()
    ymin = -5
    ymax = 40
    step = 5
  else:
    val = df_[var].mean()
    val_std = df_[var].std()
    ymin = -10
    ymax = 80
    step = 10


  return val, val_std

if __name__ == "__main__":
  main()


