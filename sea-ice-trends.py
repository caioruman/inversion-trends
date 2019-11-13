import numpy as np
import pandas as pd
import sys
import os
from datetime import date, datetime, timedelta

from glob import glob
from rpn.rpn import RPN
from rpn.domains.rotated_lat_lon import RotatedLatLon
from rpn import level_kinds

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
  folder_loc = "/home/cruman/projects/rrg-sushama-ab/teufel/"
  #PanArctic_0.5d_CanRCP45_NOCTEM_RUN/Diagnostics/PanArctic_0.5d_CanRCP45_NOCTEM_RUN_202403/pmPanArctic_0.5d_CanRCP45_NOCTEM_RUN_202403_moyenne"

  exps = ['PanArctic_0.5d_CanHisto_NOCTEM_RUN', 'PanArctic_0.5d_CanHisto_NOCTEM_R2', 'PanArctic_0.5d_CanHisto_NOCTEM_R3',
          'PanArctic_0.5d_CanHisto_NOCTEM_R4', 'PanArctic_0.5d_CanHisto_NOCTEM_R5',  'PanArctic_0.5d_CanRCP45_NOCTEM_R2', 
          'PanArctic_0.5d_CanRCP45_NOCTEM_R3', 'PanArctic_0.5d_CanRCP45_NOCTEM_R5', 'PanArctic_0.5d_CanRCP45_NOCTEM_R4', 
          'PanArctic_0.5d_CanRCP45_NOCTEM_RUN']

  etickets = ["PAN_CAN85_CT", "PAN_CAN85_R2", "PAN_CAN85_R3", "PAN_CAN85_R4", "PAN_CAN85_R5",
            "PAN_CAN45_R2", "PAN_CAN45_R3", "PAN_CAN45_R5", "PAN_CAN45_R4", "PAN_CAN45_CT"]

  datai = 1976
  dataf = 2099

  #open mask file
  f_mask = 'mask_arctic2.nc'

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

  # Pandas columns names
  colnames = ['SimName', 'CloudCover', 'SeaIce', 'ATM_H20', 'T2M', 'T2M_J8', 'Wind', 'Year', 'Month', 'Region' ]
  varnames = ['GL', 'J8', 'UU/VV', 'NF', 'IWVM']

  #df = pd.DataFrame(columns=colnames)  

  for year in range(datai, dataf+1):
    print(year)

    if os.path.exists('CSV/TimeSeries_Vars_{0}.csv'.format(year)):
      print("Already calculated")
      continue
    rows = []
    for month in range(1, 13):

    
      for exp, eticket in zip(exps, etickets):

        #nc_file = "{0}/{1}/InversionV2/Inversion_925_1000_ERA_{2}{3:02d}.nc".format(folder_loc, exp, year, month)
        if (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_RUN' and year < 2006):
          exp = 'PanArctic_0.5d_CanHisto_NOCTEM_RUN'
          eticket = "PAN_CAN85_CT"
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R2' and year < 2006):
          exp = 'PanArctic_0.5d_CanHisto_NOCTEM_R2'
          eticket = "PAN_CAN85_R2"
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R3' and year < 2006):
          exp = 'PanArctic_0.5d_CanHisto_NOCTEM_R3'
          eticket = "PAN_CAN85_R3"
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R4' and year < 2006):
          exp = 'PanArctic_0.5d_CanHisto_NOCTEM_R4'
          eticket = "PAN_CAN85_R4"
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R5' and year < 2006):
          exp = 'PanArctic_0.5d_CanHisto_NOCTEM_R5'
          eticket = "PAN_CAN85_R5"

        rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp, year, month)
        rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp, year, month)

        #print(nc_file)
        try:
          ds = RPN(rpn_file)

          var = ds.get_4d_field('NF', label=eticket)
          dates_tt = list(sorted(var.keys()))
          #key = var[dates_tt[0]].keys()[0]
          key = [*var[dates_tt[0]].keys()][0]
          var_3d = np.asarray([var[d][key] for d in dates_tt])
          cloud_cover = np.squeeze(var_3d.copy())*3600        

          seaice = np.squeeze(ds.variables["GL"][:])
          water_atm = np.squeeze(ds.variables["IWVM"][:])

          t2m_1 = np.squeeze(ds.variables["J8"][:])

          ds.close()
        except:
          # if the file don't exist, jump to the next record
          print("File {0} do not exist".format(rpn_file))
          cloud_cover = np.zeros([172,172])+np.nan
          seaice = np.zeros([172,172])+np.nan
          water_atm = np.zeros([172,172])+np.nan
          t2m_1 = np.zeros([172,172])+np.nan
          #continue
        
        

        ds = RPN(rpn_file_dm)

        var = ds.get_4d_field('TT', label=eticket)
        dates_tt = list(sorted(var.keys()))
        #key = var[dates_tt[0]].keys()[0]
        key = [*var[dates_tt[0]].keys()][0]
        var_3d = np.asarray([var[d][key] for d in dates_tt])
        t2m = np.squeeze(var_3d.copy())*3600

        uu = np.squeeze(ds.variables["UU"][:])
        vv = np.squeeze(ds.variables["VV"][:])
        uv = np.sqrt(np.power(uu, 2) + np.power(vv, 2))
        
        ds.close()        

        # looping throught the mask        
        for m in range(1, 22):
          # variables: cloud_cover, seaice, water_atm, t2m, t2m_1, uv
          #print(m) 
          #try:          
          aux_cc = np.nanmean(cloud_cover[mask == m])
          aux_seaice = np.nanmean(seaice[mask == m])
          aux_water_atm = np.nanmean(water_atm[mask == m])
          aux_t2m = np.nanmean(t2m[mask == m])
          aux_t2m_1 = np.nanmean(t2m_1[mask == m])
          aux_uv = np.nanmean(uv[mask == m])
          #except:
            # If if falls here, there's no inversion on the area             
            #print(year, month, m, exp)
            #print(nc_file)
            #print(dt[mask == m])
            #print(freq[mask == m])
            #aux_dt = 0
            #aux_freq = 0

          rows.append([exp, aux_cc, aux_seaice, aux_water_atm, aux_t2m, aux_t2m_1, aux_uv, year, month, m])
          #print([exp, aux_freq, aux_dt, year, month, m])


    df_aux = pd.DataFrame(data=rows, columns=colnames)
    #frames = [df, df_aux]
    #df = pd.concat(frames)        

        # read stuff and calculate the ensenble, store it on pandas
        # monthly and seasonal
    df_aux.to_csv('CSV/TimeSeries_Vars_{0}.csv'.format(year), encoding='utf-8')

if __name__ == "__main__":
    main()
