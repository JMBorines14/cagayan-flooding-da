from osgeo import gdal
from camodel import update_D
import numpy as np
import netCDF4 as nc
import sys

from datetime import datetime
from datetime import timedelta
from netCDF4 import date2num
from netCDF4 import Dataset

def x_coord(idx):
    return a*idx + b*idx + xoff

def y_coord(idx):
    return d*idx + e*idx + yoff

if __name__ == "__main__":
    #open the TIFF file
    dataset = gdal.Open(sys.argv[1])
    n, m, band = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount
    xoff, a, b, yoff, d, e = dataset.GetGeoTransform()

    m, n = 6050 - 6000, 4050 - 4000 #delete this
    xoff = a*6000 + b*6000 + xoff
    yoff = d*4000 + e*4000 + yoff
    print(xoff, yoff)

    #initialize output file and dimensions
    output_dataset = nc.Dataset('output.nc', 'w', format = 'NETCDF4')
    time = output_dataset.createDimension('time', None)
    lat = output_dataset.createDimension('lat', m)
    lon = output_dataset.createDimension('lon', n)

    times = output_dataset.createVariable('time', 'f8', ('time',))
    lats = output_dataset.createVariable('lat', 'f4', ('lat',))
    lons = output_dataset.createVariable('lon', 'f4', ('lon',))
    depth = output_dataset.createVariable('depth', 'f4', ('time', 'lat', 'lon',))
    depth.grid_mapping = 'phlvfour'

    phlvfour = output_dataset.createVariable('phlvfour', 'c')
    phlvfour.spatial_ref = dataset.GetProjectionRef()
    phlvfour.GeoTransform = " ".join(str(x) for x in dataset.GetGeoTransform())


    utc_now = datetime.utcnow()
    time_list = [utc_now + timedelta(hours=1*step) for step in range(100)]
    print(time_list[0], time_list[-1])
    trans_time = date2num(time_list, units="hours since 0001-01-01 00:00:00.0", calendar="gregorian")

    #output latitudes and longitudes to the dataset
    times[:] = trans_time
    lats[:] = np.array([x_coord(k) for k in range(m)])
    lons[:] = np.array([y_coord(k) for k in range(n)])

    data1 = dataset.GetRasterBand(1).ReadAsArray()
    dataset = None

    #define the surface and depth matrices
    S = np.array([list(i) for i in list(data1)])
    S = S[6000:6050, 4000:4050] #delete this
    I = np.zeros((m,n)) #I_total
    D = np.zeros((m,n))

    #initialize the rainfall distribution matrix
    R = np.zeros((m,n)) #rainfall
    R[m//2][n//2] = 100
    R[m//3][n//3] = 150

    D += R #update the depth
    L = S + D #initialize L as the sum of S and D

    for time in range(100):
        print(f'I am at time step {time}')
        I, ibabawas, idadagdag = update_D(L, D, I, m, n)
        D = D - ibabawas + idadagdag

        depth[time, :, :] = D
        R = np.zeros((m, n)) #update this to the rainfall function
        D += R
        L = S + D
    
    output_dataset.close()
    print("I am done with the simulation.")