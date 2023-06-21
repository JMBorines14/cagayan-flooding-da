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

man = 0.03
delta_X = 1 #distance
tol = 0
A = 1 #area of the cell
delta_t = 1 #delta_t is timestep
delta_e = 1 #length of the edge of the cell

def x_coord(idx):
    return a*idx + b*idx + xoff

def y_coord(idx):
    return d*idx + e*idx + yoff

def time_range_list(start_date, end_date, mins):
    time_list = []
    curr_date = start_date
    while curr_date <= end_date:
        time_list.append(curr_date)
        curr_date += timedelta(minutes=mins)
    return time_list


if __name__ == "__main__":
    # command line arguments
    demfile = sys.argv[1]       # DEM TIFF
    raindir = sys.argv[2]       # directory of rainfall TIFFs
    mins = int(sys.argv[3])     # no. of mins in each timestep
    delta_t = mins * 60

    if 180 % mins != 0:
        print("Number of minutes should have 180 as a multiple.")
        quit()

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

    start_date = datetime(2020, 11, 7, 23, 0, 0)
    end_date = datetime(2020, 11, 14, 23, 0, 0)
    time_list = time_range_list(start_date, end_date, mins)
    print(time_list[0], time_list[-1], len(time_list))
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


    R = rainfall.generate_rainfall_matrix(m, n, mins, raindir)

    D += R[0, :, :]  # update the depth
    L = S + D  # initialize L as the sum of S and D

    print("Number of time steps: " + str(R.shape[0]))

    for time in range(len(time_list)):
        print(f'I am at time step {time}')
        I, ibabawas, idadagdag = update_D(L, D, I, m, n, man, delta_X, tol, A, delta_t, delta_e)
        D = D - (ibabawas/A) + (idadagdag/A)

        depth[time, :, :] = D
        D += R[time, :, :]
        L = S + D

    output_dataset.close()
    print("I am done with the simulation.")
