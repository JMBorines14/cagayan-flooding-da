from osgeo import gdal
from osgeo import ogr
from datetime import datetime
import os
from pathlib import Path
import numpy as np
import fnmatch


def generate_rainfall_matrix(m, n, mins, directory):
    # count TIFF files in directory
    rdcount = len(fnmatch.filter(os.listdir(directory), '*.*'))
    t = int((180/mins)*(rdcount+1))

    R = np.zeros((t, m, n))

    for filename in os.listdir(directory):
        rd = gdal.Open("{d}/{fn}".format(d=directory, fn=filename))

        rainfall = rd.GetRasterBand(1).ReadAsArray()
        rd = None

        timestep = int(Path(filename).stem)

        print("Generating rainfall matrix for time step " +
              str(timestep*(int(180/mins))))

        R[timestep*(int(180/mins)), :, :] = np.array([list(i)
                                                     for i in list(rainfall)])/1000

    return R

def dam_matrix(lats, lons, time_list):
    release1 = datetime(2020, 11, 9)
