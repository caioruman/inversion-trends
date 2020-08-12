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

  datai = 1979
  dataf = 2099

  #open mask file
  f_mask = 'mask_arctic3.nc'
  sea_mask = 'MG.fst'

  ds = Dataset(f_mask)
  mask = ds.variables['tas'][:]
  lon = ds.variables['lon'][:]
  lat = ds.variables['lat'][:]

  # sea mask with values between 0 and 1
  r = RPN(sea_mask)
  mg = np.squeeze(r.variables['MG'][:])
  mg = mg[20:-20,20:-20]


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
   22: North of Laptev Sea
  '''
  # 1 = land; 0 = sea
  reg_sea_land = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0]
  ds.close()  

  # Pandas columns names
#  colnames = ['SimName', 'CloudCover', 'SeaIce', 'ATM_H20', 'T2M', 'T2M_J8', 'Wind', 'Year', 'Month', 'Region' ]
  colnames = ['SimName', 'LW_down', 'SH', 'LH', 'LH_net', 'Year', 'Month', 'Region' ]
#  varnames = ['GL', 'J8', 'UU/VV', 'NF', 'IWVM']
  varnames = ['AD', 'AH', 'AV', 'AI']


  #df = pd.DataFrame(columns=colnames)  

  for year in range(datai, dataf+1):
    print(year)

    if os.path.exists('CSV/TimeSeries_Flux_{0}.csv'.format(year)):
      print("Already calculated")
      continue
    rows = []
    for month in range(1, 13):

      change = False
      for exp, eticket in zip(exps, etickets):

        #nc_file = "{0}/{1}/InversionV2/Inversion_925_1000_ERA_{2}{3:02d}.nc".format(folder_loc, exp, year, month)
        if (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_RUN' and year < 2006):
          exp1 = 'PanArctic_0.5d_CanHisto_NOCTEM_RUN'
          eticket = "PAN_CAN85_CT"          
          rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
          rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R2' and year < 2006):
          exp1 = 'PanArctic_0.5d_CanHisto_NOCTEM_R2'
          eticket = "PAN_CAN85_R2"
          rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
          rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R3' and year < 2006):
          exp1 = 'PanArctic_0.5d_CanHisto_NOCTEM_R3'
          eticket = "PAN_CAN85_R3"        
          rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
          rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R4' and year < 2006):
          exp1 = 'PanArctic_0.5d_CanHisto_NOCTEM_R4'
          eticket = "PAN_CAN85_R4"          
          rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
          rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
        elif (exp == 'PanArctic_0.5d_CanRCP45_NOCTEM_R5' and year < 2006):
          exp1 = 'PanArctic_0.5d_CanHisto_NOCTEM_R5'
          eticket = "PAN_CAN85_R5"          
          rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
          rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp1, year, month)
        else:
          rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp, year, month)
          rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp, year, month)

        #rpn_file = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/pm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp, year, month)
        #rpn_file_dm = "{0}/{1}/Diagnostics/{1}_{2}{3:02d}/dm{1}_{2}{3:02d}_moyenne".format(folder_loc, exp, year, month)

        #print(nc_file)
        try:
          # AD, AH, AV, AI
          ds = RPN(rpn_file)

          lw_down = np.squeeze(ds.variables['AD'][:])
          SH = np.squeeze(ds.variables['AH'][:])
          LH = np.squeeze(ds.variables['AV'][:])
          lw_net = np.squeeze(ds.variables['AI'][:])

#          var = ds.get_4d_field('NF', label=eticket)
#          dates_tt = list(sorted(var.keys()))
#          #key = var[dates_tt[0]].keys()[0]
#          key = [*var[dates_tt[0]].keys()][0]
#          var_3d = np.asarray([var[d][key] for d in dates_tt])
#          cloud_cover = np.squeeze(var_3d.copy())*3600        

#          seaice = np.squeeze(ds.variables["GL"][:])
#          water_atm = np.squeeze(ds.variables["IWVM"][:])

#          t2m_1 = np.squeeze(ds.variables["J8"][:])

          ds.close()
        except:
          # if the file don't exist, jump to the next record
          print("File {0} do not exist".format(rpn_file))
#          cloud_cover = np.zeros([172,172])+np.nan
#          seaice = np.zeros([172,172])+np.nan
#          water_atm = np.zeros([172,172])+np.nan
#          t2m_1 = np.zeros([172,172])+np.nan
          lw_down = np.zeros([172,172]) + np.nan
          SH = np.zeros([172,172]) + np.nan
          LH = np.zeros([172,172]) + np.nan
          lw_net = np.zeros([172,172]) + np.nan
          #continue
                
        #ds = RPN(rpn_file_dm)

        #var = ds.get_4d_field('TT', label=eticket)
        #dates_tt = list(sorted(var.keys()))
        #key = var[dates_tt[0]].keys()[0]
        #key = [*var[dates_tt[0]].keys()][0]
        #var_3d = np.asarray([var[d][key] for d in dates_tt])
        #t2m = np.squeeze(var_3d.copy())*3600

        #uu = np.squeeze(ds.variables["UU"][:])
        #vv = np.squeeze(ds.variables["VV"][:])
        #uv = np.sqrt(np.power(uu, 2) + np.power(vv, 2))
        
        #ds.close()        

        # looping throught the mask        
        for m in range(1, 23):
          # variables: cloud_cover, seaice, water_atm, t2m, t2m_1, uv
          #print(m)
          # step 1
          aux_lwd = lw_down.copy()
          aux_sh = SH.copy()
          aux_lh = LH.copy()
          aux_lwn = lw_net.copy()

          # applying the sea ice mask over the region mask
          # regions with less than 75% land are considered water.
          if reg_sea_land[m-1] == 0: # sea
            aux_lwd[mg > 0.75] = np.nan
            aux_sh[mg > 0.75] = np.nan
            aux_lh[mg > 0.75] = np.nan
            aux_lwn[mg > 0.75] = np.nan

          else: # land
            aux_lwd[mg <= 0.75] = np.nan
            aux_sh[mg <= 0.75] = np.nan
            aux_lh[mg <= 0.75] = np.nan
            aux_lwn[mg <= 0.75] = np.nan

          aux_lw_down = np.nanmean(aux_lwd[mask == m])
          aux_SH = np.nanmean(aux_sh[mask == m])
          aux_LH = np.nanmean(aux_lh[mask == m])
          aux_lw_net = np.nanmean(aux_lwn[mask == m])

#          rows.append([exp, aux_cc, aux_seaice, aux_water_atm, aux_t2m, aux_t2m_1, aux_uv, year, month, m])
          rows.append([exp, aux_lw_down, aux_SH, aux_LH, aux_lw_net, year, month, m])
          #print([exp, aux_freq, aux_dt, year, month, m])


    df_aux = pd.DataFrame(data=rows, columns=colnames)
    #frames = [df, df_aux]
    #df = pd.concat(frames)        

        # read stuff and calculate the ensenble, store it on pandas
        # monthly and seasonal
    df_aux.to_csv('CSV/TimeSeries_Flux_{0}.csv'.format(year), encoding='utf-8')

if __name__ == "__main__":
    main()
