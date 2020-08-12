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
    Inter Annual variability of inversion characteristics and parameters that have important influence on inversions

    Saving the data in a pandas dataframe, separated by:
      - Regions according the mask file
      - Latitude Bands (to do)
      - Land / Sea (to do)
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

  #open mask file
  f_mask = 'mask_arctic3.nc'
  sea_mask = 'MG.fst'  

  ds = Dataset(f_mask)
  mask = ds.variables['tas'][:]
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]

  # due to a conversion error from rpn to nc, I need to subtract 273.15
  mask = mask - 273.15
  # I'm only interested in data in the Arctic  
  mask[lat < 60] = np.nan
  # And where mask == 0, not interested either
  mask[mask==0] = np.nan

  # sea mask with values between 0 and 1
  r = RPN(sea_mask)
  mg = np.squeeze(r.variables['MG'][:])
  mg = mg[20:-20,20:-20]

  '''
  Regions adapted from Wang and Key (2005): Arctic Surface, Cloud, and Radiation Properties Based on the AVHRR Polar Pathfinder Dataset. Part II: Recent Trends
   1: Greenland
   2: Chukchi Sea
   3: Canada Basin
   4: Central Arctic
   5: Laptev Sea
   6: North Pole
   7: Nansen Basin
   8: Barents Sea
   9: GIN Seas
   10: Baffin Bay
   11: Canada Archipelago
   12: Hudson Bay
   13: North Europe
   14: North Central Russia
   15: Northeastern Russia
   16: Alaska Region
   17: North Canada (NWT/Yukon)
   18: Beaufort Sea
   19: Baffin Island
   20: Nunavut (Continental part)
   21: Kara Sea   
   22: North of Laptev Sea
  '''
  # 1 = land; 0 = sea
  reg_sea_land = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0]
  ds.close()  

  # Pandas columns names
  colnames = ['SimName', 'FREQ', 'DT', 'Year', 'Month', 'Region' ]

  #df = pd.DataFrame(columns=colnames)  

  for year in range(datai, dataf+1):
    print(year)

    if os.path.exists('CSV/TimeSeries_Inv_RCP85_{0}.csv'.format(year)):
      print("Already calculated")
      continue
    rows = []
    for month in range(1, 13):

    
      for exp in exps:        

        nc_file = "{0}/{1}/InversionV2/Inversion_925_1000_ERA_{2}{3:02d}.nc".format(folder_loc, exp, year, month)

        #print(nc_file)
        ds = Dataset(nc_file)

        freq = np.squeeze(ds.variables["FREQ"][:])
        dt = np.squeeze(ds.variables["DT"][:])

        
        ds.close()        

        # looping throught the mask        
        for m in range(1, 23):

          #print(m) 
          try:          
            aux_dt1 = dt.copy()
            aux_freq1 = freq.copy()

            # applying the sea ice mask over the region mask
            # regions with less than 75% land are considered water.
            if reg_sea_land[m-1] == 0: # sea
              aux_dt1[mg > 0.75] == 0 
              aux_freq1[mg > 0.75] == 0
            else:
              aux_dt1[mg <= 0.75] == 0
              aux_freq1[mg <= 0.75] == 0


            aux_dt = np.nanmean(aux_dt1[mask == m])
            aux_freq = np.nanmean(aux_freq1[mask == m])
          except:
            # If if falls here, there's no inversion on the area             
            print(year, month, m, exp)
            print(nc_file)
            #print(dt[mask == m])
            #print(freq[mask == m])
            aux_dt = 0
            aux_freq = 0

          rows.append([exp, aux_freq, aux_dt, year, month, m])
          #print([exp, aux_freq, aux_dt, year, month, m])


    df_aux = pd.DataFrame(data=rows, columns=colnames)
    #frames = [df, df_aux]
    #df = pd.concat(frames)        

        # read stuff and calculate the ensenble, store it on pandas
        # monthly and seasonal
    df_aux.to_csv('CSV/TimeSeries_Inv_RCP85_{0}.csv'.format(year), encoding='utf-8')

if __name__ == "__main__":
    main()
