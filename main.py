from osgeo import gdal
from camodel import update_D
import numpy as np
import netCDF4 as nc
import sys
import rainfall

from datetime import datetime
from datetime import timedelta
from netCDF4 import date2num
from netCDF4 import Dataset


def x_coord(idx):
    return a*idx + b*idx + xoff


def y_coord(idx):
    return d*idx + e*idx + yoff


if __name__ == "__main__":
    # command line arguments
    demfile = sys.argv[1]   # DEM TIFF
    raindir = sys.argv[2]   # directory of rainfall TIFFs
    mins = int(sys.argv[3])  # no. of mins in each timestep

    dataset = gdal.Open(demfile)
    n, m, band = dataset.RasterXSize, dataset.RasterYSize, dataset.RasterCount
    xoff, a, b, yoff, d, e = dataset.GetGeoTransform()

    # initialize output file and dimensions
    output_dataset = nc.Dataset('output.nc', 'w', format='NETCDF4')
    time = output_dataset.createDimension('time', None)
    lat = output_dataset.createDimension('lat', m)
    lon = output_dataset.createDimension('lon', n)

    times = output_dataset.createVariable('time', 'f8', ('time',))
    lats = output_dataset.createVariable('lat', 'f4', ('lat',))
    lons = output_dataset.createVariable('lon', 'f4', ('lon',))
    depth = output_dataset.createVariable(
        'depth', 'f4', ('time', 'lat', 'lon',))
    depth.grid_mapping = 'phlvfour'

    phlvfour = output_dataset.createVariable('phlvfour', 'c')
    phlvfour.spatial_ref = dataset.GetProjectionRef()
    phlvfour.GeoTransform = " ".join(str(x) for x in dataset.GetGeoTransform())

    utc_now = datetime.utcnow()
    time_list = [utc_now + timedelta(hours=1*step) for step in range(100)]
    print(time_list[0], time_list[-1])
    trans_time = date2num(
        time_list, units="hours since 0001-01-01 00:00:00.0", calendar="gregorian")

    # output latitudes and longitudes to the dataset
    times[:] = trans_time
    lats[:] = np.array([x_coord(k) for k in range(m)])
    lons[:] = np.array([y_coord(k) for k in range(n)])

    data1 = dataset.GetRasterBand(1).ReadAsArray()
    dataset = None

    # define the surface and depth matrices
    S = np.array([list(i) for i in list(data1)])
    I = np.zeros((m, n))  # I_total
    D = np.zeros((m, n))

    # # initialize the rainfall distribution matrix
    # R = np.zeros((m, n))  # rainfall
    # R[m//2][n//2] = 100
    # R[m//3][n//3] = 150

    R = rainfall.generate_rainfall_matrix(m, n, mins, raindir)

    D += R[0, :, :]  # update the depth
    L = S + D  # initialize L as the sum of S and D

    print("Number of time steps: " + str(R.shape[0]))

    for time in range(10):
        print(f'I am at time step {time}')
        I, ibabawas, idadagdag = update_D(L, D, I, m, n)
        D = D - ibabawas + idadagdag

        depth[time, :, :] = D
        D += R[time, :, :]
        L = S + D

    output_dataset.close()
    print("I am done with the simulation.")
