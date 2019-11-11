import numpy as np
import pandas as pd
import sys
import os
from datetime import date, datetime, timedelta

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
  dataf = 1980

  years = range(datai, dataf+1)
  

  periods = [[12, 1, 2], [6, 7, 8]]
  p_name = ["DJF", "JJA"]

  master_list_dt = []   # Even elements: DJF; Odd elements: JJA
  master_list_freq = []

  for year in years:
    print(year)

    df = pd.read_csv('CSV/TimeSeries_Inv_RCP85_{0}.csv'.format(year), skipinitialspace=True, index_col=0)        

    for period, pname in zip(periods, p_name):    
      
      # 0, 1: mean and std for 85
      # 2, 3: mean and std for 45
      region_dt = np.zeros([21,4])
      region_freq = np.zeros([21,4])

      for region in range(1, 22):
        
        df_ = df.loc[(df['SimName'].str.contains('CanHisto')==True) & (df['Region'] == region) & (df['Month'].isin(period))]

        aux_dt, aux_dt_std, aux_freq , aux_freq_std = read_inv(df, 'CanHisto', region, period)

        region_dt[region-1, 0] = aux_dt
        region_dt[region-1, 1] = aux_dt_std

        region_freq[region-1, 0] = aux_freq
        region_freq[region-1, 1] = aux_freq_std

        aux_dt, aux_dt_std, aux_freq , aux_freq_std = read_inv(df, 'CanRCP45', region, period)

        region_dt[region-1, 2] = aux_dt
        region_dt[region-1, 3] = aux_dt_std

        region_freq[region-1, 2] = aux_freq
        region_freq[region-1, 3] = aux_freq_std

      master_list_dt.append(region_dt)    
      master_list_freq.append(region_freq)    

        
  print("Summer")
  print(master_list_dt[1::2])
  print("Winter")
  print(master_list_dt[0::2])

   
  # Plot stuff

def read_inv(df, simName, region, period):

  df_ = df.loc[(df['SimName'].str.contains(simName)==True) & (df['Region'] == region) & (df['Month'].isin(period))]

  return df_['DT'].mean(), df_['DT'].std(), df_['FREQ'].mean(), df_['FREQ'].std()

if __name__ == "__main__":
    main()
