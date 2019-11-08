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

'''

def main():

  # 1st: Read the file with the inversion strength and frequency
# /pixel/project01/cruman/ModelData/inversionv2/PanArctic_0.5d_CanRCP45_NOCTEM_R2/InversionV2/Inversion_925_1000_ERA_205804.nc
  folder_loc = "/pixel/project01/cruman/ModelData/inversionv2/"

  exps = ['PanArctic_0.5d_CanHisto_NOCTEM_RUN', 'PanArctic_0.5d_CanHisto_NOCTEM_R2', 'PanArctic_0.5d_CanHisto_NOCTEM_R3',
          'PanArctic_0.5d_CanHisto_NOCTEM_R5', 'PanArctic_0.5d_CanHisto_NOCTEM_R4']

  datai = 1976
  dataf = 2099

  for year in range(datai, dataf+1):
    for month in range(1, 13):

      for exp in exps:

        nc_file = "{0}/{1}/InversionV2/Inversion_925_1000_ERA_{2}{3:02d}.nc".format(folder_loc, exp, year, month)

        ds = Dataset(nc_file)

        freq = ds.variables["FREQ"][:]
        dt = ds.variables["DT"][:]
        # read stuff and calculate the ensenble, store it on pandas
        # monthly and seasonal
    

if __name__ == "__main__":
    main()
