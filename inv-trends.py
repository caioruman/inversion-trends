import numpy as np
import pandas as pd
import sys

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
          'PanArctic_0.5d_CanHisto_NOCTEM_R5', 'PanArctic_0.5d_CanHisto_NOCTEM_R4']

  datai = 1976
  dataf = 2099

  #open mask file
  f_mask = 'mask_arctic.nc'

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
  '''
  ds.close()  

  for year in range(datai, dataf+1):
    for month in range(1, 13):

      for exp in exps:

        nc_file = "{0}/{1}/InversionV2/Inversion_925_1000_ERA_{2}{3:02d}.nc".format(folder_loc, exp, year, month)

        ds = Dataset(nc_file)

        freq = np.squeeze(ds.variables["FREQ"][:])
        dt = np.squeeze(ds.variables["DT"][:])

        ds.close()

        # looping throught the mask
        for m in range(1, 22):
                    
          aux_dt = np.nanmean(dt[mask == m])
          aux_freq = np.nanmean(freq[mask == m])
          
          
          sys.exit()
        # read stuff and calculate the ensenble, store it on pandas
        # monthly and seasonal
    

if __name__ == "__main__":
    main()
